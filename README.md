# typing-protocol-intersection

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
```

```
> # without plugin
> mypy example.py
example.py:36: error: "ProtocolIntersection[HasX, HasY]" has no attribute "x"
example.py:36: error: "ProtocolIntersection[HasX, HasY]" has no attribute "y"
example.py:39: error: Need type annotation for "valid_o"
example.py:40: error: Argument 1 to "get_x_y_1" has incompatible type "ProtocolIntersection[ProtocolIntersection[Any, HasX], HasY]"; expected "DesiredObject"
example.py:41: error: Argument 1 to "get_x_y_2" has incompatible type "ProtocolIntersection[ProtocolIntersection[Any, HasX], HasY]"; expected "ProtocolIntersection[HasX, HasY]"
Found 5 errors in 1 file (checked 1 source file)
>
> # with plugin
> mypy example.py
Success: no issues found in 1 source file
```