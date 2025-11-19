import json
from pathlib import Path
import sqlite3
import typing as t

from behave import *  # type: ignore # Star imports are generally a bad idea, but we're doing one anyway, encouraged by Behave.
from behave.model import Table
from behave.runner import Context

from sandals.core import generate_python_from_json_data
from test.output.result import (
    DataClass,
    create_table,
    insert_records,
    select_all_records,
)
from test.util.name_storage import NameStorage


REPO_ROOT: Path = Path(__file__).parents[3]
PYTHON_RESULT_FILE_NAME = "result.py"
PYTHON_RESULT_FILE_PATH = REPO_ROOT / "test" / "output" / PYTHON_RESULT_FILE_NAME


class NameCapsule(NameStorage):
    json_schema: dict[str, t.Any]


NAME_CAP: NameCapsule = NameCapsule()


@given("the following JSON schema")
def _(ctx: Context) -> None:
    if ctx.text is None:
        raise RuntimeError("Did not find text in the context")
    NAME_CAP.json_schema = json.loads(ctx.text)  # type: ignore # Assume ctx.text is of type str.


@when("we run the generate command")
def _(ctx: Context) -> None:
    python_result: str = generate_python_from_json_data(NAME_CAP.json_schema)

    with open(PYTHON_RESULT_FILE_PATH, "w") as pf:
        pf.write(python_result)


@then("we should be able to persist the following records using the generated code")
def _(ctx: Context) -> None:
    if ctx.table is None:
        raise RuntimeError("Did not find table in the context")
    table: Table = ctx.table

    from test.output.result import PodOneToMany

    inserted, selected = _test_round_trip(PodOneToMany, table)

    assert selected == inserted, f"{selected} != {inserted}"


def _test_round_trip(cls: type[DataClass], table: Table) -> tuple[list[DataClass], list[DataClass]]:
    conn: sqlite3.Connection = sqlite3.connect(":memory:")

    create_table(conn, cls)

    inserted: list[DataClass] = [cls.from_dict(row) for row in table]
    insert_records(conn, inserted)
    selected: list[DataClass] = select_all_records(conn, cls)
    conn.close()

    return inserted, selected
