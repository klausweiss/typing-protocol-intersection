from types import SimpleNamespace
from typing import Generic, Protocol, TypeVar

from typing_protocol_intersection import ProtocolIntersection  # pylint: disable=unused-import


class HasX(Protocol):
    x: str


class HasY(Protocol):
    y: str


_T = TypeVar("_T", covariant=True)


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

    def build(self) -> _T:
        return SimpleNamespace(**self._d)  # type: ignore


class DesiredObject(HasY, HasX, Protocol):
    pass


def get_x_y(builder: Builder[DesiredObject]) -> None:
    obj = builder.build()
    print(f"x:{obj.x}; y:{obj.y}")


def main() -> None:
    builder = Builder().with_x().with_y()
    get_x_y(builder)


# expected stdout
# Success: no issues found in 1 source file
