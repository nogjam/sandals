import importlib
import inspect
import json
import typing as t


from behave import *  # type: ignore # Star imports are generally a bad idea, but we're doing one anyway, encouraged by Behave.
from behave.runner import Context

from sandals.base import BindBase
from test.util.name_storage import NameStorage


class NameCapsule(NameStorage):
    json_metadata: dict[str, t.Any]
    classes: list[type[BindBase]]


NAME_CAP: NameCapsule = NameCapsule()


@given("the following metadata and class templates in module {name}")
def _(ctx: Context, name: str) -> None:
    if ctx.text is None:
        raise RuntimeError("Did not find text in the context")

    NAME_CAP.json_metadata = json.loads(ctx.text)  # type: ignore # Assume ctx.text is of type str.

    module = importlib.import_module("test.templates.pod")
    NAME_CAP.classes = []
    for _, m in inspect.getmembers(module, inspect.isclass):
        if issubclass(m, BindBase) and m is not BindBase:
            NAME_CAP.classes.append(m)


@when("we run the generate command 2")
def _(ctx: Context) -> None:
    for c in NAME_CAP.classes:
        print(f"{c.__name__}: {", ".join(c._slots)}")

    # python_result: str = generate_python_from_json_data(NAME_CAP.json_schema)

    # with open(PYTHON_RESULT_FILE_PATH, "w") as pf:
    #     pf.write(python_result)


@then("we should be able to persist the following {class_name} records using the generated code 2")
def _(ctx: Context, class_name: str) -> None:
    pass
