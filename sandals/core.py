"""Core functionality of sandals."""

import typing as t

from sandals import config as c
from sandals.template import SQLITE_POD_TYPE_MAP, Kind
from sandals.util import pascal_case_to_snake_case


COMPOUND_FIELD_OUTER_TYPE: t.Final[str] = "list"
COMPOUND_FIELD_SQL_TYPE_PREFIX: t.Final[str] = "list["
COMPOUND_FIELD_SQL_TYPE_SUFFIX: t.Final[str] = "]"


def generate_python_from_json_data(data: dict) -> str:
    with open(c.TEMPLATE_PATH, "r") as f:
        template: str = f.read()

    return template.replace(
        f"# {c.TEMPLATE_LOC_GENERATED_CLASSES}", _generate_dataclass_code(data)
    )


def _generate_dataclass_code(data: dict) -> str:
    tab: str = " " * 4
    code: str = ""
    for c in data["classes"]:
        code += f'class {c["name"]}(DataClass):\n'

        # Class attributes
        code += f'{tab}table_name: str = "{pascal_case_to_snake_case(c["name"])}"\n'
        code += f"{tab}fields: list[Field] = [\n"
        for p in c["properties"]:
            p_name: str = p["name"]
            p_type: str = p["type"]
            field_kind: str = f"{Kind.__name__}.{Kind.POD.name}"
            pod_type: str = p_type
            if p_type.startswith(prefix := COMPOUND_FIELD_SQL_TYPE_PREFIX):
                suffix: str = COMPOUND_FIELD_SQL_TYPE_SUFFIX
                pod_type = p_type[len(prefix) : -len(suffix)]
                field_kind = f"{Kind.__name__}.{Kind.COMPOUND.name}"
            code += f'{tab}{tab}Field("{p_name}", "{SQLITE_POD_TYPE_MAP[pod_type].sql}", {field_kind}),\n'
        code += f"{tab}]\n"

        # __init__()
        code += f"\n"
        code += f"{tab}def __init__(\n"
        code += f"{tab}{tab}self,\n"
        code += f"{tab}{tab}row_id: int,\n"
        for p in c["properties"]:
            code += f"{tab}{tab}{p["name"]}: {p["type"]},\n"
        code += f"{tab}) -> None:\n"
        code += f"{tab}{tab}if not isinstance(row_id, int):\n"
        code += f"{tab}{tab}{tab}raise TypeError(\"'row_id' is not of type 'int'\")\n"
        for p in c["properties"]:
            p_type: str = p["type"]
            if p_type.startswith(prefix := COMPOUND_FIELD_SQL_TYPE_PREFIX):
                suffix: str = COMPOUND_FIELD_SQL_TYPE_SUFFIX
                pod_type: str = p_type[len(prefix) : -len(suffix)]
                outer_type: str = COMPOUND_FIELD_OUTER_TYPE
                code += f"{tab}{tab}if not isinstance({p["name"]}, {outer_type}):\n"
                code += f'{tab}{tab}{tab}raise TypeError("\'{p["name"]}\' is not of type \'{outer_type}\'")\n'
                code += f"{tab}{tab}if len({p["name"]}) > 1 and not isinstance({p["name"]}[0], {pod_type}):\n"
                code += f'{tab}{tab}{tab}raise TypeError("\'{p["name"]}\' contained type is not \'{pod_type}\'")\n'
            else:
                code += f"{tab}{tab}if not isinstance({p["name"]}, {p["type"]}):\n"
                code += f'{tab}{tab}{tab}raise TypeError("\'{p["name"]}\' is not of type \'{p["type"]}\'")\n'
        code += f"{tab}{tab}self.row_id: int = row_id\n"
        code += f"{tab}{tab}super().__init__()\n"
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

        # from_dict()
        code += f"\n"
        code += f"{tab}@classmethod\n"
        code += f'{tab}def from_dict(cls, data: dict[str, t.Any]) -> "{c["name"]}":\n'
        code += f"{tab}{tab}return {c["name"]}(**data)\n"
    return code
