# pylint: skip-file
"""
source: https://gist.github.com/evhub/5ef01a7d33582e84c9838bdbe9405cd4

Note this file won't typecheck, but it's a different issue we aim to detect is not there. Not only would the file not
typecheck, but mypy would crash with:
  AssertionError: Cannot find component 'ProtocolIntersection\u200b' for 'typing_protocol_intersection.types.ProtocolIntersection\u200b'
See https://github.com/klausweiss/typing-protocol-intersection/issues/4 for details
"""

from typing import Protocol


class X(Protocol):
    x: str


class Y(Protocol):
    y: str


class XY:
    x: str = "asdf"
    y: str = "dfaf"


class Container:
    from typing_protocol_intersection import ProtocolIntersection as _ProtocolIntersection

    ProtocolIntersection = _ProtocolIntersection


def foo(xy: Container.ProtocolIntersection[X, Y]) -> None:
    print(xy.x, xy.y)


foo(XY())
