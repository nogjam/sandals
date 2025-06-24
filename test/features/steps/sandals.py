import json

from behave import *
from behave.runner import Context

from sandals.core import generate_sql_from_json_schema_data


@given("the following JSON schema")
def _(ctx: Context, schema: str) -> None:
    ctx.schema = json.loads(schema)


@when("we run the generate command")
def _(ctx: Context) -> None:
    ctx.generate_result = generate_sql_from_json_schema_data(ctx.schema)


@then("the following SQL should be generated")
def _(ctx: Context) -> None:
    pass
