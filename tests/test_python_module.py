from typing import NamedTuple

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

from typing_protocol_intersection import ProtocolIntersection


def test_does_not_break_in_runtime():
    class ProtoX(Protocol):
        x: str

    class ProtoY(Protocol):
        y: str

    class ProtoZ(Protocol):
        z: str

    class XYZ(NamedTuple):
        x: str
        y: str
        z: str

    def concat_fields(intersection: ProtocolIntersection[ProtoX, ProtoY, ProtoZ]) -> None:
        return intersection.x + intersection.y + intersection.z

    assert concat_fields(XYZ("x", "y", "z")) == "xyz"
