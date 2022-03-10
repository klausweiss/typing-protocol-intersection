import typing
from collections import deque
from typing import Callable, Optional

import mypy.errors
import mypy.nodes
import mypy.types
from mypy.options import Options
from mypy.plugin import FunctionContext, MethodContext, Plugin

CallContext = typing.Union[MethodContext, FunctionContext]


class CustomPlugin(Plugin):
    def __init__(self, options: Options) -> None:
        super().__init__(options)

    def get_method_hook(self, fullname: str) -> Optional[Callable[[MethodContext], mypy.types.Type]]:
        return intersection_function_hook

    def get_function_hook(self, fullname: str) -> Optional[Callable[[FunctionContext], mypy.types.Type]]:
        return intersection_function_hook


class TypeInfoWrapper(typing.NamedTuple):
    type_info: mypy.nodes.TypeInfo
    base_classes: typing.List[mypy.nodes.TypeInfo]


def mk_typeinfo_wrapper() -> TypeInfoWrapper:
    defn = mypy.nodes.ClassDef(
        name="ProtocolIntersection",
        defs=mypy.nodes.Block([]),
        base_type_exprs=[mypy.nodes.NameExpr("typing.Protocol")],
        type_vars=[],
    )
    defn.fullname = "typing_protocol_intersection.types.ProtocolIntersection"
    type_info = mypy.nodes.TypeInfo(names=mypy.nodes.SymbolTable(), defn=defn, module_name="intersection")
    type_info.mro = [type_info]
    return TypeInfoWrapper(type_info, [])


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
        type_info_wrapper = self._run_fold(type_, mk_typeinfo_wrapper())
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

    def _add_type_to_intersection(
        self, intersection_type_info_wrapper: TypeInfoWrapper, typ: mypy.types.Instance
    ) -> None:
        if not typ.type.is_protocol:
            self._fail("Only Protocols can be used in ProtocolIntersection.", typ)
            return
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


def intersection_function_hook(context: CallContext) -> mypy.types.Type:
    resolver = ProtocolIntersectionResolver(context.api.fail)
    return resolver.fold_intersection_and_its_args(context.default_return_type)


def plugin(version: str) -> typing.Type[Plugin]:
    # ignore version argument if the plugin works with all mypy versions.
    return CustomPlugin
