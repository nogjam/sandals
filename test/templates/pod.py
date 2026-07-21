from datetime import datetime
import typing as t

from sandals.base import BindBase


SANDALS_VERSION_ID: t.Final[str] = "abcdefg"
SANDALS_VERSION_SEQUENCE: t.Final[int] = 1


class RadioStation(BindBase):
    count: int
    gt_hundo: bool
    number: float
    description: str
    last_listen: datetime
