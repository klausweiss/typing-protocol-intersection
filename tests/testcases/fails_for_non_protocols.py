from typing import Generic, TypeVar

from typing_protocol_intersection import ProtocolIntersection


class HasX:  # note this is not a Protocol
    x: str


T = TypeVar("T")


class Builder(Generic[T]):
    def with_x(self) -> "Builder[ProtocolIntersection[T, HasX]]":
        return self  # type: ignore


# expected stdout
# tests/testcases/fails_for_non_protocols.py:14:25: error: Only Protocols can be used in ProtocolIntersection.  [misc]
# Found 1 error in 1 file (checked 1 source file)
