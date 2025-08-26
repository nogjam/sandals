import difflib
import json

from behave import *
from behave.runner import Context

from sandals.core import generate_sql_schema_from_json_data


@given("the following JSON schema")
def _(ctx: Context) -> None:
    ctx.json_schema = json.loads(ctx.text)  # type: ignore # We can assume ctx.text is of type str.


@when("we run the generate command")
def _(ctx: Context) -> None:
    ctx.sql_result = generate_sql_schema_from_json_data(ctx.json_schema)
    ctx.python_result = generate_python_from_json_data(ctx.json_schema)


@then("the following SQL should be generated")
def _(ctx: Context) -> None:
    expected: str = ctx.text  # type: ignore # We can assume ctx.text is of type str.
    assert ctx.cmd_result.strip() == expected.strip()


@then("we should be able to persist the following records")
def _(ctx: Context) -> None:
    pass
