from typing import Any, Type


class ProtocolIntersection:
    """Intersection of a couple of Protocols. Allows to specify a type that
    conforms to multiple protocols without defining a separate class.

    Even though it doesn't derive Generic, mypy treats it as such when used
    with the typing_protocol_intersection plugin.

    Reads best when imported as `Has`.

    Example usage:
        >>> from typing_extensions import Protocol
        >>> from typing_protocol_intersection import ProtocolIntersection as Has
        >>> class X(Protocol): ...
        >>> class Y(Protocol): ...
        >>> class Z(Protocol): ...
        >>> def foo(bar: Has[X, Y, Z]) -> None:
        ...     pass

    See package's README or tests for more advanced examples.
    """

    def __class_getitem__(cls, _item: Any) -> Type["ProtocolIntersection"]:
        return cls
