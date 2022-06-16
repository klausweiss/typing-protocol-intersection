import collections
import sys
import typing
from collections import deque
from typing import Callable, Optional

import mypy.errorcodes
import mypy.errors
import mypy.nodes
import mypy.options
import mypy.plugin
import mypy.types

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import TypeGuard
else:  # pragma: no cover
    from typing_extensions import TypeGuard

SignatureContext = typing.Union[mypy.plugin.FunctionSigContext, mypy.plugin.MethodSigContext]


class ProtocolIntersectionPlugin(mypy.plugin.Plugin):
    # pylint: disable=unused-argument

    def get_type_analyze_hook(
        self, fullname: str
    ) -> Optional[Callable[[mypy.plugin.AnalyzeTypeContext], mypy.types.Type]]:
        if fullname == "typing_protocol_intersection.types.ProtocolIntersection":
            return type_analyze_hook(fullname)
        return None

    def get_method_signature_hook(
        self, fullname: str
    ) -> Optional[Callable[[mypy.plugin.MethodSigContext], mypy.types.FunctionLike]]:
        return intersection_function_signature_hook

    def get_function_signature_hook(
        self, fullname: str
    ) -> Optional[Callable[[mypy.plugin.FunctionSigContext], mypy.types.FunctionLike]]:
        return intersection_function_signature_hook


class TypeInfoWrapper(typing.NamedTuple):
    type_info: mypy.nodes.TypeInfo
    base_classes: typing.List[mypy.nodes.TypeInfo]


class IncomparableTypeName(str):
    """A string that never returns True when compared (equality) with another instance of this type."""

    def __eq__(self, x: object) -> bool:
        if isinstance(x, IncomparableTypeName):
            return False
        return super().__eq__(x)

    def __hash__(self) -> int:  # pylint: disable=useless-super-delegation
        return super().__hash__()


def mk_protocol_intersection_typeinfo(
    name: str,
    *,
    # For ProtocolIntersections to not be treated as the same type, but just as protocols,
    # their fullnames need to differ - that's why it's an IncomparableTypeName.
    fullname: IncomparableTypeName,
    symbol_table: Optional[mypy.nodes.SymbolTable] = None,
) -> mypy.nodes.TypeInfo:
    defn = mypy.nodes.ClassDef(
        name=name,
        defs=mypy.nodes.Block([]),
        base_type_exprs=[
            mypy.nodes.NameExpr("typing.Protocol"),
            # mypy expects object to be here at the last index ('we skip "object" since everyone implements it')
            mypy.nodes.NameExpr("builtins.object"),
        ],
        type_vars=[],
    )
    defn.fullname = fullname
    defn.info.is_protocol = True
    type_info = mypy.nodes.TypeInfo(
        names=symbol_table if symbol_table is not None else mypy.nodes.SymbolTable(),
        defn=defn,
        module_name="typing_protocol_intersection",
    )
    type_info.mro = [type_info]
    type_info.is_protocol = True
    return type_info


class ProtocolIntersectionResolver:
    def fold_intersection_and_its_args(self, type_: mypy.types.Type) -> mypy.types.Type:
        folded_type = self.fold_intersection(type_)
        if isinstance(folded_type, mypy.types.Instance):
            folded_type.args = tuple(self.fold_intersection(t) for t in folded_type.args)
        return folded_type

    def fold_intersection(self, type_: mypy.types.Type) -> mypy.types.Type:
        if not self._is_intersection(type_):
            return type_
        type_info = mk_protocol_intersection_typeinfo(
            "ProtocolIntersection",
            fullname=IncomparableTypeName("typing_protocol_intersection.types.ProtocolIntersection"),
        )
        type_info_wrapper = self._run_fold(type_, TypeInfoWrapper(type_info, []))
        args = [mypy.types.Instance(ti, []) for ti in type_info_wrapper.base_classes]
        return mypy.types.Instance(type_info_wrapper.type_info, args=args)

    def _run_fold(self, type_: mypy.types.Instance, intersection_type_info_wrapper: TypeInfoWrapper) -> TypeInfoWrapper:
        intersections_to_process = deque([type_])
        while intersections_to_process:
            intersection = intersections_to_process.popleft()
            for arg in intersection.args:
                if self._is_intersection(arg):
                    intersections_to_process.append(arg)
                    continue
                if isinstance(arg, mypy.types.Instance):
                    self._add_type_to_intersection(intersection_type_info_wrapper, arg)
        return intersection_type_info_wrapper

    @staticmethod
    def _add_type_to_intersection(intersection_type_info_wrapper: TypeInfoWrapper, typ: mypy.types.Instance) -> None:
        name_expr = mypy.nodes.NameExpr(typ.type.name)
        name_expr.node = typ.type
        intersection_type_info_wrapper.type_info.defn.base_type_exprs.insert(0, name_expr)
        intersection_type_info_wrapper.type_info.mro.insert(0, typ.type)
        intersection_type_info_wrapper.base_classes.insert(0, typ.type)

    @staticmethod
    def _is_intersection(typ: mypy.types.Type) -> TypeGuard[mypy.types.Instance]:
        return isinstance(typ, mypy.types.Instance) and typ.type.fullname == (
            "typing_protocol_intersection.types.ProtocolIntersection"
        )


def intersection_function_signature_hook(context: SignatureContext) -> mypy.types.FunctionLike:
    resolver = ProtocolIntersectionResolver()
    signature = context.default_signature
    signature.ret_type = resolver.fold_intersection_and_its_args(signature.ret_type)
    signature.arg_types = [resolver.fold_intersection_and_its_args(t) for t in signature.arg_types]
    return signature


def type_analyze_hook(fullname: str) -> Callable[[mypy.plugin.AnalyzeTypeContext], mypy.types.Type]:
    def _type_analyze_hook(context: mypy.plugin.AnalyzeTypeContext) -> mypy.types.Type:
        args = tuple(context.api.analyze_type(arg_t) for arg_t in context.type.args)
        base_types_of_args = set()
        for arg in args:
            if isinstance(arg, mypy.types.Instance):
                if arg.type.is_protocol:
                    base_types_of_args.update(arg.type.mro)
                else:
                    context.api.fail(
                        "Only Protocols can be used in ProtocolIntersection.", arg, code=mypy.errorcodes.VALID_TYPE
                    )
        symbol_table = mypy.nodes.SymbolTable(collections.ChainMap(*(base.names for base in base_types_of_args)))
        type_info = mk_protocol_intersection_typeinfo(
            context.type.name, fullname=IncomparableTypeName(fullname), symbol_table=symbol_table
        )
        # add base classes to MRO - this way we can support protocols inheriting one another
        # we don't really care for mro here
        type_info.mro = list(base_types_of_args) + type_info.mro
        return mypy.types.Instance(type_info, args, line=context.type.line, column=context.type.column)

    return _type_analyze_hook


def plugin(_version: str) -> typing.Type[mypy.plugin.Plugin]:
    # ignore version argument if the plugin works with all mypy versions.
    return ProtocolIntersectionPlugin
