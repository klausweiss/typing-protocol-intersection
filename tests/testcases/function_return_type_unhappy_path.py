from types import SimpleNamespace
from typing import Protocol

from typing_protocol_intersection import ProtocolIntersection


class HasX(Protocol):
    x: str


class HasY(Protocol):
    y: str


def get_o() -> ProtocolIntersection[ProtocolIntersection[None, HasY], HasY]:  # note: no HasX
    return SimpleNamespace(x="x", y="y")  # type: ignore


class DesiredObject(HasX, HasY, Protocol):
    pass


def get_x_y(o: DesiredObject) -> None:
    print(f"{o.x=}; {o.y=}")


def main() -> None:
    invalid_o = get_o()
    get_x_y(invalid_o)


# expected stdout
# tests/testcases/function_return_type_unhappy_path.py:29: error: Argument 1 to "get_x_y" has incompatible type "ProtocolIntersection[HasY, HasY]"; expected "DesiredObject"
# tests/testcases/function_return_type_unhappy_path.py:29: note: "ProtocolIntersection" is missing following "DesiredObject" protocol member:
# tests/testcases/function_return_type_unhappy_path.py:29: note:     x
# Found 1 error in 1 file (checked 1 source file)
