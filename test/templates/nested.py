import typing as t

from sandals.base import BindBase


SANDALS_VERSION_ID: t.Final[str] = "abcdefg"
SANDALS_VERSION_SEQUENCE: t.Final[int] = 1


class Fruit(BindBase):
    name: str
    color: str


class Tree(BindBase):
    classification: str
    fruit: Fruit
