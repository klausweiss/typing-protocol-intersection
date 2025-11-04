from types import SimpleNamespace
from typing import Generic, Protocol, TypeVar

from typing_protocol_intersection import ProtocolIntersection


class HasX(Protocol):
    x: str


class HasY(Protocol):
    y: str


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

    def build(self) -> _T:
        return SimpleNamespace(**self._d)  # type: ignore


class DesiredObject(HasX, HasY, Protocol):
    pass


def get_x_y_1(obj: DesiredObject) -> None:
    print(f"x:{obj.x}; y:{obj.y}")


def get_x_y_2(obj: ProtocolIntersection[HasX, HasY]) -> None:
    print(f"x:{obj.x}; y:{obj.y}")


def main() -> None:
    invalid_o = Builder().with_x().build()
    get_x_y_1(invalid_o)
    get_x_y_2(invalid_o)


# expected stdout
# tests/testcases/in_generic_param_unhappy_path.py:49:15: error: Argument 1 to "get_x_y_1" has incompatible type "ProtocolIntersection[HasX]"; expected "DesiredObject"  [arg-type]
# tests/testcases/in_generic_param_unhappy_path.py:49:15: note: "ProtocolIntersection" is missing following "DesiredObject" protocol member:
# tests/testcases/in_generic_param_unhappy_path.py:49:15: note:     y
# tests/testcases/in_generic_param_unhappy_path.py:50:15: error: Argument 1 to "get_x_y_2" has incompatible type "typing_protocol_intersection.types.ProtocolIntersection[HasX]"; expected "typing_protocol_intersection.types.ProtocolIntersection[HasY, HasX]"  [arg-type]
# tests/testcases/in_generic_param_unhappy_path.py:50:15: note: "ProtocolIntersection" is missing following "ProtocolIntersection" protocol member:
# tests/testcases/in_generic_param_unhappy_path.py:50:15: note:     y
# Found 2 errors in 1 file (checked 1 source file)
