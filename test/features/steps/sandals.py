import json
import typing as t

from behave import *  # type: ignore # Star imports are generally a bad idea, but we're doing one anyway, encouraged by Behave.
from behave.runner import Context

from sandals.core import (
    generate_python_from_json_data,
    generate_sql_schema_from_json_data,
)
from test.util.name_storage import NameStorage


class NameCapsule(NameStorage):
    json_schema: dict[str, t.Any]
    python_result: str
    sql_result: str


NAME_CAP: NameCapsule = NameCapsule()


@given("the following JSON schema")
def _(ctx: Context) -> None:
    NAME_CAP.json_schema = json.loads(ctx.text)  # type: ignore # Assume ctx.text is of type str.


@when("we run the generate command")
def _(ctx: Context) -> None:
    NAME_CAP.sql_result = generate_sql_schema_from_json_data(NAME_CAP.json_schema)
    NAME_CAP.python_result = generate_python_from_json_data(NAME_CAP.json_schema)


@then("the following SQL should be generated")
def _(ctx: Context) -> None:
    expected: str = ctx.text  # type: ignore # We can assume ctx.text is of type str.
    actual: str = NAME_CAP.sql_result.strip(" \n")
    expected = expected.strip(" \n")
    assert actual == expected, f"{actual} != {expected}"


@then("we should be able to persist the following records")
def _(ctx: Context) -> None:
    pass
