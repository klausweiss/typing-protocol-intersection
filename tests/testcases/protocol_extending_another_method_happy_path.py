from typing import Protocol

from typing_protocol_intersection import ProtocolIntersection as Has


class Base(Protocol):
    def base(self) -> None: ...


class X(Base, Protocol):  # pylint: disable=invalid-name
    x: str


class Y(Protocol):  # pylint: disable=invalid-name
    y: str


class Impl:
    x = "x"
    y = "y"

    def base(self) -> None:
        print("Impl")


def get_x_y(obj: Has[X, Y]) -> None:
    obj.base()
    print(f"x:{obj.x}; y:{obj.y}")


def main() -> None:
    valid_o = Impl()
    get_x_y(valid_o)


# expected stdout
# Success: no issues found in 1 source file
