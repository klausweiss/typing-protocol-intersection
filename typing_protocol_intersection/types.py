from typing import Any, Type


class ProtocolIntersection:
    """
    Intersection of a couple of Protocols. Allows to specify a type that
    conforms to multiple protocols without defining a separate class.

    Even though it doesn't derive Generic, mypy treats it as such when used
    with the typing_protocol_intersection plugin.

    Example usage:
        >>> from typing_extensions import Protocol
        >>> class HasX(Protocol): ...
        >>> class HasY(Protocol): ...
        >>> class HasZ(Protocol): ...
        >>> def foo(x: ProtocolIntersection[HasX, HasY, HasZ]) -> None:
        ...     pass

    See package's README or tests for more advanced examples.
    """

    def __class_getitem__(cls, item: Any) -> Type["ProtocolIntersection"]:
        pass
