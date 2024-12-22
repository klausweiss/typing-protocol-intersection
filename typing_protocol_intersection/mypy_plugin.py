import collections
import sys
import typing
from collections import deque
from itertools import takewhile
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
AnyContext = typing.Union[SignatureContext, mypy.plugin.AnalyzeTypeContext]


class ProtocolIntersectionPlugin(mypy.plugin.Plugin):
    # pylint: disable=unused-argument

    def report_config_data(self, ctx: mypy.plugin.ReportConfigContext) -> int:
        # Whatever this method returns is used by mypy to determine whether a module should be checked again or if a
        # cache-loaded info will do. If the obtained value is different from the previous one, cache is invalidated.
        #
        # As far as this plugin is concerned, this method is only used to aid generation of `UniqueFullname`s. If it
        # wasn't for this method, mypy couldn't identify where a runtime-generated class name comes from, as it looks up
        # the class names in the cache (and subsequently crashes when it fails to find them).
        return UniqueFullname.instance_counter

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
    # base_classes need to only contain the direct base classes - they are used when pretty-printing the name of a
    # concrete ProtocolIntersection
    base_classes: typing.List[mypy.nodes.TypeInfo]


class UniqueFullname(str):
    """A string that has a suffix consisting of zero-width spaces.

    Each instance created has more ZWSPs appended than the previously
    created one. This is a hack to get class fullnames that are all
    different from each other. We need this so that all
    ProtocolIntersections are treated as separate classes, and not as
    instances of the same class.

    We could just override __eq__, and in fact that's what's been here
    before, but mypyc has an  optimization that treats all str
    subclasses as strs when comparing. Distributions of mypy are
    compiled with that optimization enabled, which used to break the
    plugin.
    """

    ZERO_WIDTH_SPACE = "\u200B"
    instance_counter: typing.ClassVar[int] = 0

    def __new__(cls, base_fullname: str) -> "UniqueFullname":
        cls.instance_counter += 1

        # This is a very naive implementation. We could encode the suffix with more invisible characters, but for
        # simplicity let's keep it as is, unless it turns out that the performance suffers a lot.
        invisible_suffix = cls.instance_counter * cls.ZERO_WIDTH_SPACE
        return super().__new__(cls, base_fullname + invisible_suffix)


def mk_protocol_intersection_typeinfo(
    name: str,
    *,
    # For ProtocolIntersections to not be treated as the same type, but just as protocols,
    # their fullnames need to differ - that's why it's a UniqueFullname.
    fullname: UniqueFullname,
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
    def __init__(self, context: SignatureContext) -> None:
        super().__init__()
        self._context = context

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
            fullname=UniqueFullname("typing_protocol_intersection.types.ProtocolIntersection"),
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
                    if not arg.type.is_protocol:
                        _error_non_protocol_member(arg, context=self._context)
                    self._add_type_to_intersection(intersection_type_info_wrapper, arg)
        return intersection_type_info_wrapper

    @staticmethod
    def _add_type_to_intersection(intersection_type_info_wrapper: TypeInfoWrapper, typ: mypy.types.Instance) -> None:
        # We might be interested in modifying another properties too (like
        # intersection_type_info_wrapper.type_info.defn.base_type_exprs), but up until now it seems what we have is
        # enough. Keep number of modified properties as low as possible (so that it's manageable).
        #
        # We also don't check for is_protocol in the bae classes - mypy doesn't allow protocol to have non-protocol base
        # classes anyway and for direct ProtocolIntersection type arguments we do the check in type_analyze_hook.
        intersection_type_info_wrapper.type_info.mro = [
            base for base in typ.type.mro if base not in intersection_type_info_wrapper.type_info.mro
        ] + intersection_type_info_wrapper.type_info.mro
        intersection_type_info_wrapper.base_classes.insert(0, typ.type)

    @staticmethod
    def _is_intersection(typ: mypy.types.Type) -> TypeGuard[mypy.types.Instance]:
        return isinstance(typ, mypy.types.Instance) and typ.type.fullname.startswith(
            "typing_protocol_intersection.types.ProtocolIntersection"
        )


def intersection_function_signature_hook(context: SignatureContext) -> mypy.types.FunctionLike:
    resolver = ProtocolIntersectionResolver(context)
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
                    _error_non_protocol_member(arg, context=context)
        symbol_table = mypy.nodes.SymbolTable(collections.ChainMap(*(base.names for base in base_types_of_args)))
        type_info = mk_protocol_intersection_typeinfo(
            context.type.name, fullname=UniqueFullname(fullname), symbol_table=symbol_table
        )
        # add base classes to MRO - this way we can support protocols inheriting one another
        # we don't really care for mro here
        type_info.mro = list(base_types_of_args) + type_info.mro
        return mypy.types.Instance(type_info, args, line=context.type.line, column=context.type.column)

    return _type_analyze_hook


def _error_non_protocol_member(arg: mypy.types.Type, *, context: AnyContext) -> None:
    context.api.fail("Only Protocols can be used in ProtocolIntersection.", arg, code=mypy.errorcodes.VALID_TYPE)


def plugin(version: str) -> typing.Type[mypy.plugin.Plugin]:
    version_prefix, *_ = version.split("dev.", maxsplit=1)  # stripping +dev.f6a8037cc... suffix if applicable
    numeric_prefixes = (_numeric_prefix(x) for x in version_prefix.split("."))
    parted_version = tuple(int(prefix) if prefix else None for prefix in numeric_prefixes)
    if (len(parted_version) == 2 and (0, 920) <= parted_version <= (0, 991)) or (
        len(parted_version) == 3 and (1, 0, 0) <= parted_version < (1, 15, 0)
    ):
        return ProtocolIntersectionPlugin

    raise NotImplementedError(f"typing-protocol-intersection does not support mypy=={version}")


def _numeric_prefix(string: str) -> Optional[str]:
    return "".join(takewhile(str.isdigit, string))
