"""Core functionality of sandals."""

import inspect
from types import ModuleType
import typing as t

from sandals import config as c
from sandals.base import BindBase
from sandals.template import SQLITE_POD_TYPE_MAP, Kind
from sandals.util import pascal_case_to_snake_case


def _line_number_of_member_def(member: type) -> int:
    return inspect.getsourcelines(member)[1]


def _get_members_in_order_of_definition(module: ModuleType) -> list[type]:
    return sorted(
        (x[1] for x in inspect.getmembers(module, inspect.isclass)),
        key=_line_number_of_member_def,
    )


def generate_python_from_class_definitions(module: ModuleType) -> str:
    classes: list[type[BindBase]] = []
    for m in _get_members_in_order_of_definition(module):
        if issubclass(m, BindBase) and m is not BindBase:
            classes.append(m)

    return generate_python_from_template_classes(classes)


def generate_python_from_template_classes(
    template_classes: list[type[BindBase]],
) -> str:
    with open(c.TEMPLATE_PATH, "r") as f:
        template: str = f.read()

    return template.replace(
        f"# {c.TEMPLATE_LOC_GENERATED_CLASSES}",
        _generate_dataclass_code(template_classes),
    )


def _generate_dataclass_code(tcs: list[type[BindBase]]) -> str:
    tab: str = " " * 4
    code: str = ""
    first: bool = True
    for c in tcs:
        if not first:
            code += "\n\n"
        first = False

        code += f"class {c.__name__}(DataClass):\n"

        # Class attributes
        code += f'{tab}table_name: str = "{pascal_case_to_snake_case(c.__name__)}"\n'
        code += f"{tab}fields: list[Field] = [\n"
        annotations: dict[str, type] = inspect.get_annotations(c)
        p_name: str
        p_type: type
        for p_name, p_type in annotations.items():
            field_kind: str = f"{Kind.__name__}.{Kind.POD.name}"
            inner_type: type = p_type
            if p_type in tcs:
                field_kind = Kind.__name__ + "." + Kind.DC.name
            elif t.get_origin(p_type) is list:
                # Assume there is only one argument to the list type
                inner_type = t.get_args(p_type)[0]
                field_kind = (
                    Kind.__name__
                    + "."
                    + (
                        Kind.STRUCTURED.name
                        if inner_type in SQLITE_POD_TYPE_MAP
                        else Kind.COMPOUND.name
                    )
                )
            sql_type: str = (
                SQLITE_POD_TYPE_MAP[inner_type].sql
                if inner_type in SQLITE_POD_TYPE_MAP
                else "--"
            )
            code += f'{tab}{tab}Field("{p_name}", {inner_type.__name__}, "{sql_type}", {field_kind}),\n'
        code += f"{tab}]\n"

        # __init__()
        code += f"\n"
        code += f"{tab}def __init__(\n"
        code += f"{tab}{tab}self,\n"
        for p_name, p_type in annotations.items():
            code += f"{tab}{tab}{p_name}: {p_type.__name__},\n"
        code += f"{tab}{tab}row_id: int = -1,\n"
        code += f"{tab}) -> None:\n"
        for p_name, p_type in annotations.items():
            if t.get_origin(p_type) is list:
                outer_type: str = "list"
                # Assume there is only one argument to the list type
                inner_type = t.get_args(p_type)[0]
                code += f"{tab}{tab}if not isinstance({p_name}, {outer_type}):\n"
                code += f"{tab}{tab}{tab}raise TypeError(f\"'{p_name}' is of type {{type({p_name}).__name__}}, not {outer_type}\")\n"
                code += f"{tab}{tab}if len({p_name}) > 1 and not isinstance({p_name}[0], {inner_type.__name__}):\n"
                code += f"{tab}{tab}{tab}raise TypeError(f\"'{p_name}' contained type is {{type({p_name}[0]).__name__}}, not {inner_type.__name__}\")\n"
            else:
                code += f"{tab}{tab}if not isinstance({p_name}, {p_type.__name__}):\n"
                code += f"{tab}{tab}{tab}raise TypeError(f\"'{p_name}' is of type {{type({p_name}).__name__}}, not {p_type.__name__}\")\n"
        code += f"{tab}{tab}if not isinstance(row_id, int):\n"
        code += f"{tab}{tab}{tab}raise TypeError(f\"'row_id' is of type {{type(row_id).__name__}}, not int\")\n"
        code += f"{tab}{tab}self.row_id: int = row_id\n"
        for p_name in annotations.keys():
            code += f"{tab}{tab}self.{p_name} = {p_name}\n"

        # __repr__()
        code += f"\n"
        code += f"{tab}def __repr__(self) -> str:\n"
        code += f'{tab}{tab}return f"{{type(self).__name__}}(row_id={{self.row_id}}, {", ".join(f"{p_name}={{self.{p_name}}}" for p_name in annotations.keys())})"\n'

        # __eq__()
        code += f"\n"
        code += f'{tab}def __eq__(self, other: "{c.__name__}") -> bool:\n'
        code += f"{tab}{tab}return all(getattr(self, f.name) == getattr(other, f.name) for f in self.fields)\n"

    return code
