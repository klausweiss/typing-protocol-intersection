from typing import Generic, Protocol, TypeVar

from typing_protocol_intersection import ProtocolIntersection as Has


class Base(Protocol):
    def base(self) -> None: ...


class X(Base, Protocol):  # pylint: disable=invalid-name
    x: str


class Y(Protocol):  # pylint: disable=invalid-name
    y: str


T = TypeVar("T")


class Builder(Generic[T]):
    def with_x(self, value: str) -> "Builder[Has[T, X]]":
        self.__dict__["x"] = value
        return self  # type:ignore[return-value]

    def with_y(self, value: str) -> "Builder[Has[T, Y]]":
        self.__dict__["y"] = value
        return self  # type:ignore[return-value]

    def build(self) -> T:
        class Impl:
            x = self.__dict__["x"]
            y = self.__dict__["y"]

            def base(self) -> None:
                print("impl")

        return Impl()  # type:ignore[return-value]


def get_x_y(builder: Builder[Has[X, Y]]) -> None:
    obj = builder.build()
    obj.base()
    print(f"x:{obj.x}; y:{obj.y}")


def main() -> None:
    valid_o = Builder().with_x("x").with_y("y")
    get_x_y(valid_o)


# expected stdout
# Success: no issues found in 1 source file
