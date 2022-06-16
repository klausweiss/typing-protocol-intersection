from types import SimpleNamespace
from typing import Protocol

from typing_protocol_intersection import ProtocolIntersection


class HasX(Protocol):
    x: str


class HasY(Protocol):
    y: str


def get_o() -> ProtocolIntersection[HasY]:  # note: no HasX
    return SimpleNamespace(x="x", y="y")  # type: ignore


class DesiredObject(HasX, HasY, Protocol):
    pass


def get_x_y(obj: DesiredObject) -> None:
    print(f"x:{obj.x}; y:{obj.y}")


def main() -> None:
    invalid_o = get_o()
    get_x_y(invalid_o)


# expected stdout
# tests/testcases/function_return_type_unhappy_path.py:29:13: error: Argument 1 to "get_x_y" has incompatible type "ProtocolIntersection[HasY]"; expected "DesiredObject"  [arg-type]
# tests/testcases/function_return_type_unhappy_path.py:29:13: note: "ProtocolIntersection" is missing following "DesiredObject" protocol member:
# tests/testcases/function_return_type_unhappy_path.py:29:13: note:     x
# Found 1 error in 1 file (checked 1 source file)
