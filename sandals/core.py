"""Core functionality of sandals."""

import inspect
from types import ModuleType
import typing as t

from sandals import config as c
from sandals.base import BindBase
from sandals.template import MARSHAL_METHOD_NAME, SQLITE_POD_TYPE_MAP, Kind
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
    for tc in tcs:
        if not first:
            code += "\n\n"
        first = False

        is_pod_wrapper: bool = hasattr(tc, MARSHAL_METHOD_NAME)

        if is_pod_wrapper:
            code += f"class {tc.__name__}({c.CLASS_NAME_POD_WRAPPER}):\n"
        else:
            code += f"class {tc.__name__}({c.CLASS_NAME_DATA_CLASS}):\n"

        # Class attributes

        if not is_pod_wrapper:
            code += (
                f'{tab}table_name: str = "{pascal_case_to_snake_case(tc.__name__)}"\n'
            )

        code += f"{tab}fields: list[Field] = [\n"
        annotations: dict[str, type] = inspect.get_annotations(tc)
        p_name: str
        p_type: type
        for p_name, p_type in annotations.items():
            field_kind: str = f"{Kind.__name__}.{Kind.POD.name}"
            inner_type: type = p_type
            pod_type: type | None = None

            if p_type in tcs:
                field_kind = Kind.__name__ + "." + Kind.DC.name
            elif t.get_origin(p_type) is list:
                # Assume there is only one argument to the list type
                inner_type = t.get_args(p_type)[0]

                if hasattr(inner_type, MARSHAL_METHOD_NAME):
                    pod_type = inspect.signature(
                        getattr(inner_type, MARSHAL_METHOD_NAME)
                    ).return_annotation
                elif inner_type in SQLITE_POD_TYPE_MAP:
                    pod_type = inner_type

                field_kind = (
                    Kind.__name__
                    + "."
                    + (
                        Kind.STRUCTURED.name
                        if pod_type is not None
                        else Kind.COMPOUND.name
                    )
                )
            else:
                pod_type = inner_type

            sql_type: str = (
                SQLITE_POD_TYPE_MAP[pod_type].sql if pod_type is not None else "--"
            )

            code += f'{tab}{tab}Field("{p_name}", {inner_type.__name__}, "{sql_type}", {field_kind}),\n'

        code += f"{tab}]\n"

        # __init__()

        code += f"\n"
        code += f"{tab}def __init__(\n"
        code += f"{tab}{tab}self,\n"
        for p_name, p_type in annotations.items():
            if t.get_origin(p_type) is list:
                outer_type: str = "list"
                # Assume there is only one argument to the list type
                inner_type = t.get_args(p_type)[0]
                code += f"{tab}{tab}{p_name}: {outer_type}[{inner_type.__name__}],\n"
            else:
                code += f"{tab}{tab}{p_name}: {p_type.__name__},\n"
        if not is_pod_wrapper:
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
        if not is_pod_wrapper:
            code += f"{tab}{tab}if not isinstance(row_id, int):\n"
            code += f"{tab}{tab}{tab}raise TypeError(f\"'row_id' is of type {{type(row_id).__name__}}, not int\")\n"
            code += f"{tab}{tab}self.row_id: int = row_id\n"
        for p_name, p_type in annotations.items():
            if t.get_origin(p_type) is list:
                outer_type: str = "list"
                # Assume there is only one argument to the list type
                inner_type = t.get_args(p_type)[0]
                code += f"{tab}{tab}self.{p_name}: {outer_type}[{inner_type.__name__}] = {p_name}\n"
            else:
                code += f"{tab}{tab}self.{p_name}: {p_type.__name__} = {p_name}\n"

        # __repr__()

        code += f"\n"
        code += f"{tab}def __repr__(self) -> str:\n"
        code += f'{tab}{tab}return f"{{type(self).__name__}}('
        if not is_pod_wrapper:
            code += f"row_id={{self.row_id}}, "
        code += f'{", ".join(f"{p_name}={{self.{p_name}}}" for p_name in annotations.keys())})"\n'

        # __eq__()

        code += f"\n"
        code += f'{tab}def __eq__(self, other: "{tc.__name__}") -> bool:\n'
        code += f"{tab}{tab}return all(getattr(self, f.name) == getattr(other, f.name) for f in self.fields)\n"

        # Custom methods

        # ASSUMPTION: All data class attributes are defined immediately under
        # the class declaration. Custom methods are anything defined after the
        # first blank line encountered in the class' source code.
        source_lines: list[str] = inspect.getsourcelines(tc)[0]
        try:
            idx_first_blank_line: int = source_lines.index("\n")
        except ValueError:
            idx_first_blank_line: int = -1
        if idx_first_blank_line >= 0:
            code += "".join(source_lines[idx_first_blank_line:])

    return code
