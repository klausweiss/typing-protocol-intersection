from typing import Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


# Although there are only 2 type parameters here, mypy plugin overrides this
# to allow for an arbitrary number of type parameters, so constructs like
#
#   ProtocolIntersection[HasW, HasX, HasY, HasZ]
#
# are perfectly fine.
class ProtocolIntersection(Generic[T, U]):
    pass
