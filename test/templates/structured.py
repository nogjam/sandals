import typing as t

from sandals.base import BindBase


SANDALS_VERSION_ID: t.Final[str] = "abcdefg"
SANDALS_VERSION_SEQUENCE: t.Final[int] = 1


class CastOfCharacters(BindBase):
    monikers: list[str]
    ages: list[int]
