from typing import Generic, TypeVar

from typing_protocol_intersection import ProtocolIntersection


class NotProtocol:
    pass


T = TypeVar("T")


class Noop(Generic[T]):
    @classmethod
    def noop(cls, value: T) -> ProtocolIntersection[T]:
        return value


np = Noop[NotProtocol].noop(NotProtocol())
