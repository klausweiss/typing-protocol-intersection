import typing
from typing import Optional, Callable

import mypy.nodes
import mypy.types
from mypy.options import Options
from mypy.plugin import Plugin, MethodContext, FunctionContext
from mypy.types import Type
import mypy.errors

Context = typing.Union[MethodContext, FunctionContext]


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


def _add_type_to_intersection(
    intersection_type_info_wrapper: TypeInfoWrapper, typ: mypy.types.Instance, context: Context
) -> None:
    if not typ.type.is_protocol:
        context.api.fail("Only Protocols can be used in ProtocolIntersection.", typ)
        return
    name_expr = mypy.nodes.NameExpr(typ.type.name)
    name_expr.node = typ.type
    intersection_type_info_wrapper.type_info.defn.base_type_exprs.append(name_expr)
    intersection_type_info_wrapper.type_info.mro.append(typ.type)
    intersection_type_info_wrapper.base_classes.append(typ.type)


def _fold_intersection(
    intersection: mypy.types.Type, intersection_type_info_wrapper: TypeInfoWrapper, context: Context
) -> TypeInfoWrapper:
    if not isinstance(intersection, mypy.types.Instance):
        context.api.fail("Both Intersection's typevars should be a type instances!", intersection)
        return intersection_type_info_wrapper
    if not intersection.args:
        return intersection_type_info_wrapper
    l, r = intersection.args
    recurse_left = is_intersection(l)
    if not recurse_left and isinstance(l, mypy.types.Instance):
        _add_type_to_intersection(intersection_type_info_wrapper, l, context)
    recurse_right = is_intersection(r)
    if not recurse_right and isinstance(r, mypy.types.Instance):
        _add_type_to_intersection(intersection_type_info_wrapper, r, context)

    if not recurse_right and not recurse_left:
        return intersection_type_info_wrapper
    elif not recurse_right:
        return _fold_intersection(l, intersection_type_info_wrapper, context)
    elif not recurse_left:
        return _fold_intersection(r, intersection_type_info_wrapper, context)
    else:
        return _fold_intersection(l, _fold_intersection(r, intersection_type_info_wrapper, context), context)


def is_intersection(typ: mypy.types.Type) -> bool:
    return (
        isinstance(typ, mypy.types.Instance)
        and typ.type.fullname == "typing_protocol_intersection.types.ProtocolIntersection"
    )


def fold_intersection(context: Context) -> mypy.types.Type:
    t = context.default_return_type
    type_info_wrapper = _fold_intersection(t, mk_typeinfo_wrapper(), context)
    args = [mypy.types.Instance(ti, []) for ti in type_info_wrapper.base_classes]
    return mypy.types.Instance(type_info_wrapper.type_info, args=args)


def intersection_method_hook(context: Context) -> mypy.types.Type:
    if is_intersection(context.default_return_type):
        return fold_intersection(context)
    return context.default_return_type


def plugin(version: str) -> typing.Type[Plugin]:
    # ignore version argument if the plugin works with all mypy versions.
    return CustomPlugin
