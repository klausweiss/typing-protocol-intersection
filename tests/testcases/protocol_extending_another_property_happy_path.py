from typing import Protocol

from typing_protocol_intersection import ProtocolIntersection as Has


class Base(Protocol):
    base: str


class X(Base, Protocol):
    x: str


class Y(Protocol):
    y: str


class Impl:
    x = "x"
    y = "y"
    base = "base"


def get_x_y(obj: Has[X, Y]) -> None:
    print(f"x:{obj.x}; y:{obj.y}, base:{obj.base}")


def main() -> None:
    valid_o = Impl()
    get_x_y(valid_o)


# expected stdout
# Success: no issues found in 1 source file
