from typing import Dict, Generic, Protocol, TypeVar

from typing_protocol_intersection import ProtocolIntersection


class HasX(Protocol):
    x: str


class HasY(Protocol):
    y: str


T = TypeVar("T", covariant=True)


class Builder(Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self._d: Dict[str, str] = {}

    def with_x(self) -> "Builder[ProtocolIntersection[T, HasX]]":
        self._d["x"] = "X"
        return self  # type: ignore

    def with_y(self) -> "Builder[ProtocolIntersection[T, HasY]]":
        self._d["y"] = "Y"
        return self  # type: ignore

    def build(self) -> T:
        return SimpleNamespace(**self._d)  # type: ignore


class DesiredObject(HasY, HasX, Protocol):
    pass


def get_x_y(b: Builder[DesiredObject]) -> None:
    o = b.build()
    print("x:{x}; y:{y}".format(x=o.x, y=o.x))


def main() -> None:
    builder = Builder().with_x().with_y()
    get_x_y(builder)


# expected stdout
# Success: no issues found in 1 source file
