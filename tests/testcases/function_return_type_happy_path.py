from types import SimpleNamespace
from typing import Protocol

from typing_protocol_intersection import ProtocolIntersection


class HasX(Protocol):
    x: str


class HasY(Protocol):
    y: str


def get_o() -> ProtocolIntersection[HasX, HasY]:
    return SimpleNamespace(x="x", y="y")  # type: ignore


class DesiredObject(HasX, HasY, Protocol):
    pass


def get_x_y(obj: DesiredObject) -> None:
    print(f"x:{obj.x}; y:{obj.y}")


def main() -> None:
    valid_o = get_o()
    get_x_y(valid_o)


# expected stdout
# Success: no issues found in 1 source file
