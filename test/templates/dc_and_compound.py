import typing as t

from sandals.base import BindBase


SANDALS_VERSION_ID: t.Final[str] = "abcdefg"
SANDALS_VERSION_SEQUENCE: t.Final[int] = 1


class Shape(BindBase):
    name: str
    n_sides: int


class Item(BindBase):
    name: str
    price: float


class Box(BindBase):
    color: str
    shape: Shape
    items: list[Item]
