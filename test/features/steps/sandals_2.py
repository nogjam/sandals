import importlib
from pathlib import Path
import sqlite3
from types import ModuleType

from behave import *  # type: ignore # Star imports are generally a bad idea, but we're doing one anyway, encouraged by Behave.
from behave.model import Table
from behave.runner import Context

from sandals.core_2 import generate_python_from_class_definitions
from test.util.name_storage import NameStorage


REPO_ROOT: Path = Path(__file__).parents[3]
PYTHON_RESULT_FILE_NAME = "result.py"
PYTHON_RESULT_FILE_PATH = REPO_ROOT / "test" / "output" / PYTHON_RESULT_FILE_NAME


class NameCapsule(NameStorage):
    module: ModuleType


NAME_CAP: NameCapsule = NameCapsule()


@given("metadata and class definitions in module {mod_name}")
def _(ctx: Context, mod_name: str) -> None:
    NAME_CAP.module = importlib.import_module(mod_name)


@when("we run the generate command 2")
def _(ctx: Context) -> None:
    python_result: str = generate_python_from_class_definitions(NAME_CAP.module)

    with open(PYTHON_RESULT_FILE_PATH, "w") as pf:
        pf.write(python_result)


@then(
    "we should be able to persist the following {class_name} records using the generated code 2"
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
            case "RadioStation":
                return [
                    cls.from_dict_with_cast(
                        {
                            "count": row["count"],
                            "gt_hundo": row["gt_hundo"],
                            "number": row["number"],
                            "description": row["description"],
                        }
                    )
                    for row in table
                ]
            case "CastOfCharacters":
                return [
                    cls.from_dict_with_cast(
                        {
                            "monikers": [x.strip() for x in row["monikers"].split(",")],
                            "ages": [x.strip() for x in row["ages"].split(",")],
                        }
                    )
                    for row in table
                ]
            case "NumberSequence":
                return [
                    cls.from_dict_with_cast(
                        {
                            "title": row["title"],
                            "integers": [i.strip() for i in row["integers"].split(",")],
                        }
                    )
                    for row in table
                ]
            case "Tree":
                tree_fruits: list[tuple[result.Tree, str]] = []
                fruits: dict[str, result.Fruit] = {}
                for row in table:
                    if row["type"] == result.Tree.__name__:
                        tree_fruits.append(
                            (
                                result.Tree.from_dict_with_cast(
                                    dict(
                                        classification=row["classification"],
                                        fruit=dict(name="", color=""),
                                    )
                                ),
                                row["fruit"],
                            )
                        )
                    elif row["type"] == result.Fruit.__name__:
                        fruits[row["name"]] = result.Fruit.from_dict_with_cast(
                            dict(name=row["name"], color=row["color"])
                        )
                trees: list[result.Tree] = []
                for tree, fruit_name in tree_fruits:
                    tree.fruit = fruits[fruit_name]
                    trees.append(tree)
                return trees
            case "Box":
                box_shape_items: list[tuple[result.Box, str, list[str]]] = []
                items: dict[str, result.Item] = {}
                shapes: dict[str, result.Shape] = {}
                for row in table:
                    if row["type"] == result.Box.__name__:
                        box_shape_items.append(
                            (
                                result.Box.from_dict_with_cast(
                                    dict(
                                        color=row["color"],
                                        shape=dict(name="", n_sides=0),
                                        items=[],
                                    )
                                ),
                                row["shape"],
                                [x.strip() for x in row["items"].split(",")],
                            )
                        )
                    elif row["type"] == result.Item.__name__:
                        items[row["name"]] = result.Item.from_dict_with_cast(
                            dict(name=row["name"], price=row["price"])
                        )
                    elif row["type"] == result.Shape.__name__:
                        shapes[row["name"]] = result.Shape.from_dict_with_cast(
                            dict(name=row["name"], n_sides=row["n_sides"])
                        )
                boxes: list[result.Box] = []
                for box, shape_name, item_names in box_shape_items:
                    box.items = [items[name] for name in item_names]
                    box.shape = shapes[shape_name]
                    boxes.append(box)
                return boxes
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

    for i, pair in enumerate(zip(selected, inserted)):
        sel, ins = pair
        assert sel == ins, f"{i}: {sel} != {ins}"
