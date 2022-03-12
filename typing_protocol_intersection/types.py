from typing import Any, Type


class ProtocolIntersection:
    def __class_getitem__(cls, item: Any) -> "Type[ProtocolIntersection]":
        pass
