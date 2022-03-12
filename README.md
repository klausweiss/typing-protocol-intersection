# typing-protocol-intersection

[![tests & static analysis](https://github.com/klausweiss/typing-protocol-intersection/actions/workflows/ci.yml/badge.svg)](https://github.com/klausweiss/typing-protocol-intersection/actions/workflows/ci.yml)


## Installation

```shell
> pip install typing-protocol-intersection 
```

## Configuration

```shell
> cat mypy.ini
[mypy]
plugins = typing_protocol_intersection.mypy_plugin
```

## Example

### Valid program

Here's what you can write with the help of this mypy plugin:

```python
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

def get_x_y_1(o: DesiredObject) -> None:
    print(f"{o.x=}; {o.y=}")

def get_x_y_2(o: ProtocolIntersection[HasX, HasY]) -> None:
    print(f"{o.x=}; {o.y=}")

def main() -> None:
    valid_o = Builder().with_x().with_y().build()
    get_x_y_1(valid_o)
    get_x_y_2(valid_o)

if __name__ == "__main__":
    main()
```

```shell
> # without plugin
> mypy example.py
example.py:18:25: error: "ProtocolIntersection" expects no type arguments, but 2 given  [type-arg]
example.py:22:25: error: "ProtocolIntersection" expects no type arguments, but 2 given  [type-arg]
example.py:35:18: error: "ProtocolIntersection" expects no type arguments, but 2 given  [type-arg]
example.py:36:11: error: "ProtocolIntersection" has no attribute "x"  [attr-defined]
example.py:36:11: error: "ProtocolIntersection" has no attribute "y"  [attr-defined]
example.py:40:15: error: Argument 1 to "get_x_y_1" has incompatible type "ProtocolIntersection"; expected "DesiredObject"  [arg-type]
Found 6 errors in 1 file (checked 1 source file)

> # with plugin
> mypy example.py
Success: no issues found in 1 source file
```

### Invalid program

And here's how would the plugin help if you forgot to include one of the protocols:

```python
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

def get_x_y_1(o: DesiredObject) -> None:
    print(f"{o.x=}; {o.y=}")

def get_x_y_2(o: ProtocolIntersection[HasX, HasY]) -> None:
    print(f"{o.x=}; {o.y=}")

def main() -> None:
    valid_o = Builder().with_x().build()  # <-- note no .with_y()
    get_x_y_1(valid_o)
    get_x_y_2(valid_o)

if __name__ == "__main__":
    main()
```

```shell
> mypy example.py
example.py:40:15: error: Argument 1 to "get_x_y_1" has incompatible type "ProtocolIntersection[HasX]"; expected "DesiredObject"  [arg-type]
example.py:40:15: note: "ProtocolIntersection" is missing following "DesiredObject" protocol member:
example.py:40:15: note:     y
example.py:41:15: error: Argument 1 to "get_x_y_2" has incompatible type "typing_protocol_intersection.types.ProtocolIntersection[HasX]"; expected "typing_protocol_intersection.types.ProtocolIntersection[HasY, HasX]"  [arg-type]
example.py:41:15: note: "ProtocolIntersection" is missing following "ProtocolIntersection" protocol member:
example.py:41:15: note:     y
Found 2 errors in 1 file (checked 1 source file)
```