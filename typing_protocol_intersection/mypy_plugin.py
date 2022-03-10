import typing
from collections import deque
from typing import Callable, Optional

import mypy.errors
import mypy.nodes
import mypy.options
import mypy.plugin
import mypy.types

SignatureContext = typing.Union[mypy.plugin.FunctionSigContext, mypy.plugin.MethodSigContext]


class ProtocolIntersectionPlugin(mypy.plugin.Plugin):
    def get_type_analyze_hook(
        self, fullname: str
    ) -> Optional[Callable[[mypy.plugin.AnalyzeTypeContext], mypy.types.Type]]:
        if fullname == "typing_protocol_intersection.types.ProtocolIntersection":
            return type_analyze_hook(fullname)
        return None

    def get_method_signature_hook(
        self, fullname: str
    ) -> Optional[Callable[[mypy.plugin.MethodSigContext], mypy.plugin.FunctionLike]]:
        return intersection_function_signature_hook

    def get_function_signature_hook(
        self, fullname: str
    ) -> Optional[Callable[[mypy.plugin.FunctionSigContext], mypy.plugin.FunctionLike]]:
        return intersection_function_signature_hook


class TypeInfoWrapper(typing.NamedTuple):
    type_info: mypy.nodes.TypeInfo
    base_classes: typing.List[mypy.nodes.TypeInfo]


def mk_protocol_typeinfo(
    name: str, *, fullname: Optional[str] = None, symbol_table: Optional[mypy.nodes.SymbolTable] = None
) -> mypy.nodes.TypeInfo:
    defn = mypy.nodes.ClassDef(
        name=name,
        defs=mypy.nodes.Block([]),
        base_type_exprs=[mypy.nodes.NameExpr("typing.Protocol")],
        type_vars=[],
    )
    defn.fullname = name if fullname is None else fullname
    type_info = mypy.nodes.TypeInfo(
        names=symbol_table if symbol_table is not None else mypy.nodes.SymbolTable(),
        defn=defn,
        module_name="typing_protocol_intersection",
    )
    type_info.mro = [type_info]
    return type_info


class ProtocolIntersectionResolver:
    def __init__(self, fail: Callable[[str, mypy.nodes.Context], None]) -> None:
        self._fail = fail

    def fold_intersection_and_its_args(self, type_: mypy.types.Type) -> mypy.types.Type:
        folded_type = self.fold_intersection(type_)
        if isinstance(folded_type, mypy.types.Instance):
            folded_type.args = tuple(self.fold_intersection(t) for t in folded_type.args)
        return folded_type

    def fold_intersection(self, type_: mypy.types.Type) -> mypy.types.Type:
        if not self._is_intersection(type_):
            return type_
        type_info = mk_protocol_typeinfo(
            "ProtocolIntersection", fullname="typing_protocol_intersection.types.ProtocolIntersection"
        )
        type_info_wrapper = self._run_fold(type_, TypeInfoWrapper(type_info, []))
        args = [mypy.types.Instance(ti, []) for ti in type_info_wrapper.base_classes]
        return mypy.types.Instance(type_info_wrapper.type_info, args=args)

    def _run_fold(self, type_: mypy.types.Type, intersection_type_info_wrapper: TypeInfoWrapper) -> TypeInfoWrapper:
        intersections_to_process = deque([type_])
        while intersections_to_process:
            intersection = intersections_to_process.popleft()

            if not isinstance(intersection, mypy.types.Instance):
                self._fail("All of Intersection's typevars should be a type instances!", type_)
                return intersection_type_info_wrapper

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
        intersection_type_info_wrapper.type_info.defn.base_type_exprs.append(name_expr)
        intersection_type_info_wrapper.type_info.mro.append(typ.type)
        intersection_type_info_wrapper.base_classes.append(typ.type)

    @staticmethod
    def _is_intersection(typ: mypy.types.Type) -> bool:
        return (
            isinstance(typ, mypy.types.Instance)
            and typ.type.fullname == "typing_protocol_intersection.types.ProtocolIntersection"
        )


def intersection_function_signature_hook(context: SignatureContext) -> mypy.plugin.FunctionLike:
    resolver = ProtocolIntersectionResolver(context.api.fail)
    signature = context.default_signature
    signature.ret_type = resolver.fold_intersection_and_its_args(signature.ret_type)
    signature.arg_types = [resolver.fold_intersection_and_its_args(t) for t in signature.arg_types]
    return signature


def type_analyze_hook(fullname: str) -> Callable[[mypy.plugin.AnalyzeTypeContext], mypy.types.Type]:
    def _type_analyze_hook(context: mypy.plugin.AnalyzeTypeContext) -> mypy.types.Type:
        args = tuple(context.api.analyze_type(arg_t) for arg_t in context.type.args)
        symbol_table = mypy.nodes.SymbolTable()
        for arg in args:
            if isinstance(arg, mypy.types.Instance):
                if not arg.type.is_protocol:
                    context.api.fail("Only Protocols can be used in ProtocolIntersection.", arg)
                symbol_table.update(arg.type.names)
        type_info = mk_protocol_typeinfo(context.type.name, fullname=fullname, symbol_table=symbol_table)
        t = context.type
        return mypy.types.Instance(type_info, args, line=t.line, column=t.column)

    return _type_analyze_hook


def plugin(version: str) -> typing.Type[mypy.plugin.Plugin]:
    # ignore version argument if the plugin works with all mypy versions.
    return ProtocolIntersectionPlugin
