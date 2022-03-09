import typing
from typing import Optional, Callable

import mypy.nodes
import mypy.types
from mypy.options import Options
from mypy.plugin import Plugin, MethodContext, FunctionContext
from mypy.types import Type


class CustomPlugin(Plugin):
    def __init__(self, options: Options) -> None:
        super().__init__(options)

    def get_method_hook(self, fullname: str) -> Optional[Callable[[MethodContext], mypy.types.Type]]:
        return intersection_method_hook

    def get_function_hook(self, fullname: str) -> Optional[Callable[[FunctionContext], Type]]:
        return intersection_method_hook


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
    defn.fullname = "ProtocolIntersection"
    type_info = mypy.nodes.TypeInfo(names=mypy.nodes.SymbolTable(), defn=defn, module_name="intersection")
    type_info.mro = [type_info]
    return TypeInfoWrapper(type_info, [])


def _add_type_to_intersection(intersection_type_info_wrapper: TypeInfoWrapper, typ: mypy.types.Type) -> None:
    if not isinstance(typ, mypy.types.Instance):
        return
    name_expr = mypy.nodes.NameExpr(typ.type.name)
    name_expr.node = typ.type
    intersection_type_info_wrapper.type_info.defn.base_type_exprs.append(name_expr)
    intersection_type_info_wrapper.type_info.mro.append(typ.type)
    intersection_type_info_wrapper.base_classes.append(typ.type)


def _fold_intersection(
    intersection: mypy.types.Type, intersection_type_info_wrapper: TypeInfoWrapper
) -> TypeInfoWrapper:
    if not isinstance(intersection, mypy.types.Instance):
        raise TypeError("Both Intersection's typevars should be a type instances!")
    if not intersection.args:
        return intersection_type_info_wrapper
    l, r = intersection.args
    recurse_left = is_intersection(l)
    if not recurse_left and not isinstance(l, mypy.types.UninhabitedType):
        _add_type_to_intersection(intersection_type_info_wrapper, l)
    recurse_right = is_intersection(r)
    if not recurse_right and not isinstance(r, mypy.types.UninhabitedType):
        _add_type_to_intersection(intersection_type_info_wrapper, r)

    if not recurse_right and not recurse_left:
        return intersection_type_info_wrapper
    elif not recurse_right:
        return _fold_intersection(l, intersection_type_info_wrapper)
    elif not recurse_left:
        return _fold_intersection(r, intersection_type_info_wrapper)
    else:
        return _fold_intersection(l, _fold_intersection(r, intersection_type_info_wrapper))


def is_intersection(typ: mypy.types.Type) -> bool:
    return (
        isinstance(typ, mypy.types.Instance)
        and typ.type.fullname == "typing_protocol_intersection.types.ProtocolIntersection"
    )


def fold_intersection(t: mypy.types.Type) -> mypy.types.Type:
    type_info_wrapper = _fold_intersection(t, mk_typeinfo_wrapper())
    args = [mypy.types.Instance(ti, []) for ti in type_info_wrapper.base_classes]
    return mypy.types.Instance(type_info_wrapper.type_info, args=args)


def intersection_method_hook(context: typing.Union[MethodContext, FunctionContext]) -> mypy.types.Type:
    if is_intersection(context.default_return_type):
        return fold_intersection(context.default_return_type)
    return context.default_return_type


def plugin(version: str) -> typing.Type[Plugin]:
    # ignore version argument if the plugin works with all mypy versions.
    return CustomPlugin
