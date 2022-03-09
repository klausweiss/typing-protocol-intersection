from typing import TypeVar, Generic

T = TypeVar("T")
U = TypeVar("U")


class ProtocolIntersection(Generic[T, U]):
    pass
