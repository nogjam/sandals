"""Core functionality of sandals."""

import typing as t

from sandals import config as c
from sandals.template import SQLITE_POD_TYPE_MAP, Kind
from sandals.util import pascal_case_to_snake_case


STRUCTURED_FIELD_OUTER_TYPE: t.Final[str] = "list"
STRUCTURED_FIELD_SQL_TYPE_PREFIX: t.Final[str] = "list["
STRUCTURED_FIELD_SQL_TYPE_SUFFIX: t.Final[str] = "]"


def generate_python_from_json_data(data: dict) -> str:
    with open(c.TEMPLATE_PATH, "r") as f:
        template: str = f.read()

    return template.replace(
        f"# {c.TEMPLATE_LOC_GENERATED_CLASSES}", _generate_dataclass_code(data)
    )


def _generate_dataclass_code(data: dict) -> str:
    tab: str = " " * 4
    code: str = ""
    first: bool = True
    class_names: list[str] = [c["name"] for c in data["classes"]]
    for c in data["classes"]:
        if not first:
            code += "\n\n"
        first = False

        code += f'class {c["name"]}(DataClass):\n'

        # Class attributes
        code += f'{tab}table_name: str = "{pascal_case_to_snake_case(c["name"])}"\n'
        code += f"{tab}fields: list[Field] = [\n"
        for p in c["properties"]:
            p_name: str = p["name"]
            p_type: str = p["type"]
            field_kind: str = f"{Kind.__name__}.{Kind.POD.name}"
            inner_type: str = p_type
            if p_type in class_names:
                field_kind = Kind.__name__ + "." + Kind.DC.name
            elif p_type.startswith(prefix := STRUCTURED_FIELD_SQL_TYPE_PREFIX):
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
        code += f'{tab}def __eq__(self, other: "{c["name"]}") -> bool:\n'
        code += f"{tab}{tab}return all(getattr(self, f.name) == getattr(other, f.name) for f in self.fields)\n"

    return code
