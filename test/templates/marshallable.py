import typing as t

from sandals.base import BindBase


SANDALS_VERSION_ID: t.Final[str] = "abcdefg"
SANDALS_VERSION_SEQUENCE: t.Final[int] = 1


class Amount(BindBase):
    milliunits: int

    def marshal(self) -> int:
        return self.milliunits

    @property
    def dollars(self) -> int:
        return self.milliunits // 1_000

    @property
    def cents(self) -> int:
        return (self.milliunits % 1_000) // 10

    def get_deposit_str(self) -> str:
        return f"Deposit ${self.dollars}.{self.cents:>02}"


class Account(BindBase):
    number: int
    transactions: list[Amount]
