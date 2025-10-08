"""Utilities UTs."""

import pytest

from . import util


@pytest.mark.parametrize(
    ["s", "expected"],
    [
        # Don't do this.
        ("SQLSchema", "s_q_l_schema"),
        # Do this.
        ("SqlSchema", "sql_schema"),
    ],
)
def test_pascal_case_to_snake_case(s: str, expected: str) -> None:
    assert util.pascal_case_to_snake_case(s) == expected
