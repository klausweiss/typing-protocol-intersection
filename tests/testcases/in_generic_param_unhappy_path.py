from types import SimpleNamespace
from typing import Protocol, Generic, TypeVar, Dict

from typing_protocol_intersection import ProtocolIntersection


class HasX(Protocol):
    x: str


class HasY(Protocol):
    y: str


T = TypeVar("T")


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


class DesiredObject(HasX, HasY, Protocol):
    pass


def get_x_y(o: DesiredObject) -> None:
    print(f"{o.x=}; {o.y=}")


def main() -> None:
    invalid_o: DesiredObject = Builder().with_x().build()
    get_x_y(invalid_o)


# expected stdout
# tests/testcases/in_generic_param_unhappy_path.py:44: error: Incompatible types in assignment (expression has type "Intersection[HasX]", variable has type "DesiredObject")
# tests/testcases/in_generic_param_unhappy_path.py:44: note: "Intersection" is missing following "DesiredObject" protocol member:
# tests/testcases/in_generic_param_unhappy_path.py:44: note:     y
# Found 1 error in 1 file (checked 1 source file)
