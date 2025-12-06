import importlib
import json
from pathlib import Path
import sqlite3
import typing as t

from behave import *  # type: ignore # Star imports are generally a bad idea, but we're doing one anyway, encouraged by Behave.
from behave.model import Table
from behave.runner import Context

from sandals.core import generate_python_from_json_data
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


@then(
    "we should be able to persist the following {class_name} records using the generated code"
)
def _(ctx: Context, class_name: str) -> None:
    if ctx.table is None:
        raise RuntimeError("Did not find table in the context")
    table: Table = ctx.table

    from test.output import result

    # Reload to get newly generated content after previous test scenarios have
    # run.
    importlib.reload(result)

    def _get_dict_data_from_table(
        cls: type[result.DataClass], table: Table
    ) -> list[result.DataClass]:
        match class_name:
            case "SimpleData":
                return [
                    cls.from_dict_with_cast(
                        {
                            "count": row["count"],
                            "number": row["number"],
                            "description": row["description"],
                        }
                    )
                    for row in table
                ]
            case "PodOneToMany":
                return [
                    cls.from_dict_with_cast(
                        {
                            "title": row["title"],
                            "integers": [i.strip() for i in row["integers"].split(",")],
                        }
                    )
                    for row in table
                ]
            case _:
                return []

    def _test_round_trip[T: result.DataClass](
        cls: type[T], table: Table
    ) -> tuple[list[result.DataClass], list[result.DataClass]]:
        conn: sqlite3.Connection = sqlite3.connect(":memory:")

        result.create_table(conn, cls)

        inserted: list[result.DataClass] = _get_dict_data_from_table(cls, table)
        result.insert_records(conn, inserted)
        selected: list[result.DataClass] = result.select_all_records(conn, cls)
        conn.close()

        return inserted, selected

    inserted, selected = _test_round_trip(getattr(result, class_name), table)

    assert selected == inserted, f"{selected} != {inserted}"
