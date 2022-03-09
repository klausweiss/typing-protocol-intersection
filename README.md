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

def get_x_y(o: DesiredObject) -> None:
    print(f"{o.x=}; {o.y=}")

def main() -> None:
    valid_o: DesiredObject = Builder().with_x().with_y().build()
    get_x_y(valid_o)
```

```
> # without plugin
> mypy example.py
example.py:36: error: Incompatible types in assignment (expression has type "ProtocolIntersection[ProtocolIntersection[<nothing>, HasX], HasY]", variable has type "DesiredObject")
Found 1 error in 1 file (checked 1 source file)
>
> # with plugin
> mypy example.py
Success: no issues found in 1 source file
```