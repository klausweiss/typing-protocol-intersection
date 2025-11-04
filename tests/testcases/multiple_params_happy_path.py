from types import SimpleNamespace
from typing import Generic, Protocol, TypeVar

from typing_protocol_intersection import ProtocolIntersection


class HasX(Protocol):
    x: str


class HasY(Protocol):
    y: str


class HasZ(Protocol):
    z: str


_T = TypeVar("_T")


class Builder(Generic[_T]):
    def __init__(self) -> None:
        super().__init__()
        self._d: dict[str, str] = {}

    def with_x(self) -> "Builder[ProtocolIntersection[_T, HasX]]":
        self._d["x"] = "X"
        return self  # type: ignore

    def with_y(self) -> "Builder[ProtocolIntersection[_T, HasY]]":
        self._d["y"] = "Y"
        return self  # type: ignore

    def with_z(self) -> "Builder[ProtocolIntersection[_T, HasZ]]":
        self._d["z"] = "Z"
        return self  # type: ignore

    def build(self) -> _T:
        return SimpleNamespace(**self._d)  # type: ignore


def get_x_y_z(obj: ProtocolIntersection[HasX, HasY, HasZ]) -> None:
    print(f"x:{obj.x}; y:{obj.y}; z:{obj.z}")


def main() -> None:
    valid_o = Builder().with_x().with_y().with_z().build()
    get_x_y_z(valid_o)


# expected stdout
# Success: no issues found in 1 source file
