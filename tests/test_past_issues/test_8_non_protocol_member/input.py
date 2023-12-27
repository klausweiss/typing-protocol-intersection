from typing import Generic, TypeVar

from typing_protocol_intersection import ProtocolIntersection


class NotProtocol:
    pass


T = TypeVar("T")


class Noop(Generic[T]):
    @classmethod
    def noop(cls, t: T) -> ProtocolIntersection[T]:
        return t


np = Noop[NotProtocol].noop(NotProtocol())
