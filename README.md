# typing-protocol-intersection

[![tests & static analysis](https://github.com/klausweiss/typing-protocol-intersection/actions/workflows/ci.yml/badge.svg)](https://github.com/klausweiss/typing-protocol-intersection/actions/workflows/ci.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/typing-protocol-intersection)](https://pypi.org/project/typing-protocol-intersection/)

A tiny Python 3 package that introduces Protocol intersections (for `Protocol`s themselves
see [PEP 544](https://peps.python.org/pep-0544/)).
The `ProtocolIntersection` type tells mypy that an object implements multiple protocols.
It can be used either as a function parameter or as a return value.
A mypy plugin that ships with the package is required for this to work.
See the [examples](#examples) section below.

## Supported versions

The plugin supports python 3.9 up to 3.13 and mypy >= 0.920 and <= 1.14.x.

## Installation

The `typing-protocol-intersection` package is pip-installable:

```shell
pip install typing-protocol-intersection 
```

## Configuration

Add `typing_protocol_intersection.mypy_plugin` to `plugins` in mypy configuration:

```shell
> cat mypy.ini
[mypy]
plugins = typing_protocol_intersection.mypy_plugin
```

## Examples

### Simple example

```python
from typing import Protocol
from typing_protocol_intersection import ProtocolIntersection as Has

class X(Protocol):
    x: str

class Y(Protocol):
    y: str

def foo(xy: Has[X, Y]) -> None:
    # Note xy implements both X and Y, not just one of them
    print(xy.x, xy.y)
```

### Complex example - valid program

Here's a more complex example showing what you can write with the help of this mypy plugin:

```python
from types import SimpleNamespace
from typing import Protocol, Generic, TypeVar, Dict
from typing_protocol_intersection import ProtocolIntersection as Has

class X(Protocol):
    x: str

class Y(Protocol):
    y: str

T = TypeVar("T")

class Builder(Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self._d: Dict[str, str] = {}

    def with_x(self) -> "Builder[Has[T, X]]":
        self._d["x"] = "X"
        return self  # type: ignore

    def with_y(self) -> "Builder[Has[T, Y]]":
        self._d["y"] = "Y"
        return self  # type: ignore

    def build(self) -> T:
        return SimpleNamespace(**self._d)  # type: ignore

class DesiredObject(X, Y, Protocol):
    pass

def get_x_y_1(o: DesiredObject) -> None:
    print(f"{o.x=}; {o.y=}")

def get_x_y_2(o: Has[X, Y]) -> None:
    print(f"{o.x=}; {o.y=}")

def main() -> None:
    valid_o = Builder().with_x().with_y().build()
    get_x_y_1(valid_o)
    get_x_y_2(valid_o)

if __name__ == "__main__":
    main()
```

```shell
> # with plugin
> mypy example.py
Success: no issues found in 1 source file
```

### Complex example - invalid program

And here's how would the plugin help if you forgot to include one of the protocols while building an object:

```python
from types import SimpleNamespace
from typing import Protocol, Generic, TypeVar, Dict
from typing_protocol_intersection import ProtocolIntersection as Has

class X(Protocol):
    x: str

class Y(Protocol):
    y: str

T = TypeVar("T")

class Builder(Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self._d: Dict[str, str] = {}

    def with_x(self) -> "Builder[Has[T, X]]":
        self._d["x"] = "X"
        return self  # type: ignore

    def with_y(self) -> "Builder[Has[T, Y]]":
        self._d["y"] = "Y"
        return self  # type: ignore

    def build(self) -> T:
        return SimpleNamespace(**self._d)  # type: ignore

class DesiredObject(X, Y, Protocol):
    pass

def get_x_y_1(o: DesiredObject) -> None:
    print(f"{o.x=}; {o.y=}")

def get_x_y_2(o: Has[X, Y]) -> None:
    print(f"{o.x=}; {o.y=}")

def main() -> None:
    valid_o = Builder().with_x().build()  # <-- note no .with_y()
    get_x_y_1(valid_o)
    get_x_y_2(valid_o)

if __name__ == "__main__":
    main()
```

```shell
> # Note the real output would contain some invisible characters which were removed here.
> mypy example.py
example.py:40:15: error: Argument 1 to "get_x_y_1" has incompatible type "ProtocolIntersection[X]"; expected "DesiredObject"  [arg-type]
example.py:40:15: note: "ProtocolIntersection" is missing following "DesiredObject" protocol member:
example.py:40:15: note:     y
example.py:41:15: error: Argument 1 to "get_x_y_2" has incompatible type "typing_protocol_intersection.types.ProtocolIntersection[X]"; expected "typing_protocol_intersection.types.ProtocolIntersection[Y, X]"  [arg-type]
example.py:41:15: note: "ProtocolIntersection" is missing following "ProtocolIntersection" protocol member:
example.py:41:15: note:     y
Found 2 errors in 1 file (checked 1 source file)
```

## Recommended usage

The `ProtocolIntersection` class name might seem a bit lengthy, but it's explicit, which is good.
For brevity and better readability, it's recommended to use an alias when importing, as seen in the examples above.

```python
from typing_protocol_intersection import ProtocolIntersection as Has
```
