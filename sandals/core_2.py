"""Core functionality of sandals."""

import typing as t

from sandals import config as c
from sandals.base import BindBase
from sandals.template import SQLITE_POD_TYPE_MAP, Kind
from sandals.util import pascal_case_to_snake_case


STRUCTURED_FIELD_OUTER_TYPE: t.Final[str] = "list"
STRUCTURED_FIELD_SQL_TYPE_PREFIX: t.Final[str] = "list["
STRUCTURED_FIELD_SQL_TYPE_SUFFIX: t.Final[str] = "]"


def generate_python_from_template_classes(tcs: list[type[BindBase]]) -> str:
    with open(c.TEMPLATE_PATH, "r") as f:
        template: str = f.read()

    return template.replace(
        f"# {c.TEMPLATE_LOC_GENERATED_CLASSES}", _generate_dataclass_code(tc)
    )


def _generate_dataclass_code(tcs: list[type[BindBase]]) -> str:
    tab: str = " " * 4
    code: str = ""
    first: bool = True
    for c in tcs:
        if not first:
            code += "\n\n"
        first = False

        code += f'class {c.__name__}(DataClass):\n'

        # Class attributes
        code += f'{tab}table_name: str = "{pascal_case_to_snake_case(c.__name__)}"\n'
        code += f"{tab}fields: list[Field] = [\n"
        for k, v in c.__annotations__.items():
            p_name: str = k
            p_type: type = v
            field_kind: str = f"{Kind.__name__}.{Kind.POD.name}"
            inner_type: str = v.__name__
            if p_type in tcs:
                field_kind = Kind.__name__ + "." + Kind.DC.name
            elif t.get_origin(p_type) is list:
                suffix: str = STRUCTURED_FIELD_SQL_TYPE_SUFFIX
                inner_type = p_type[len(prefix) : -len(suffix)]
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
            code += f'{tab}{tab}Field("{p_name}", {inner_type}, "{sql_type}", {field_kind}),\n'
        code += f"{tab}]\n"

        # __init__()
        code += f"\n"
        code += f"{tab}def __init__(\n"
        code += f"{tab}{tab}self,\n"
        for p in c["properties"]:
            code += f"{tab}{tab}{p["name"]}: {p["type"]},\n"
        code += f"{tab}{tab}row_id: int = -1,\n"
        code += f"{tab}) -> None:\n"
        for p in c["properties"]:
            p_name: str = p["name"]
            p_type: str = p["type"]
            if p_type.startswith(prefix := STRUCTURED_FIELD_SQL_TYPE_PREFIX):
                suffix: str = STRUCTURED_FIELD_SQL_TYPE_SUFFIX
                inner_type: str = p_type[len(prefix) : -len(suffix)]
                outer_type: str = STRUCTURED_FIELD_OUTER_TYPE
                code += f"{tab}{tab}if not isinstance({p_name}, {outer_type}):\n"
                code += f"{tab}{tab}{tab}raise TypeError(f\"'{p_name}' is of type {{type({p_name}).__name__}}, not {outer_type}\")\n"
                code += f"{tab}{tab}if len({p_name}) > 1 and not isinstance({p_name}[0], {inner_type}):\n"
                code += f"{tab}{tab}{tab}raise TypeError(f\"'{p_name}' contained type is {{type({p_name}[0]).__name__}}, not {inner_type}\")\n"
            else:
                code += f"{tab}{tab}if not isinstance({p_name}, {p_type}):\n"
                code += f'{tab}{tab}{tab}raise TypeError(f"\'{p_name}\' is of type {{type({p_name}).__name__}}, not {p["type"]}")\n'
        code += f"{tab}{tab}if not isinstance(row_id, int):\n"
        code += f"{tab}{tab}{tab}raise TypeError(f\"'row_id' is of type {{type(row_id).__name__}}, not int\")\n"
        code += f"{tab}{tab}self.row_id: int = row_id\n"
        for p in c["properties"]:
            code += f"{tab}{tab}self.{p["name"]}: {p["type"]} = {p["name"]}\n"

        # __repr__()
        code += f"\n"
        code += f"{tab}def __repr__(self) -> str:\n"
        code += f'{tab}{tab}return f"{{type(self).__name__}}(row_id={{self.row_id}}, {", ".join(f"{p["name"]}={{self.{p["name"]}}}" for p in c["properties"])})"\n'

        # __eq__()
        code += f"\n"
        code += f'{tab}def __eq__(self, other: "{c.__name__}") -> bool:\n'
        code += f"{tab}{tab}return all(getattr(self, f.name) == getattr(other, f.name) for f in self.fields)\n"

    return code
