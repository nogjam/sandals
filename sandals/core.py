"""Core functionality of sandals."""

from sandals import config as c
from sandals.util import pascal_case_to_snake_case


tab: str = " " * 2
type_map: dict[str, str] = {"int": "INTEGER", "float": "REAL", "str": "TEXT"}


def generate_python_from_json_data(data: dict) -> str:
    with open(c.TEMPLATE_PATH, "r") as f:
        template: str = f.read()

    return template.replace(
        f"# {c.TEMPLATE_LOC_GENERATED_CLASSES}", _generate_dataclass_code(data)
    )


SQLITE_TYPE_MAPPING: dict[str, str] = {
    "int": "INTEGER",
    "float": "REAL",
    "str": "TEXT",
}


def _generate_dataclass_code(data: dict) -> str:
    tab: str = " " * 4
    code: str = ""
    for c in data["classes"]:
        code += f'class {c["name"]}(DataClass):\n'

        # Class attributes
        code += f'{tab}table_name: str = "{pascal_case_to_snake_case(c["name"])}"\n'
        code += f"{tab}fields: list[Field] = [\n"
        for p in c["properties"]:
            code += (
                f'{tab}{tab}Field("{p["name"]}", "{SQLITE_TYPE_MAPPING[p["type"]]}"),\n'
            )
        code += f"{tab}]\n"
        code += f"\n"

        # __init__()
        code += f"{tab}def __init__(\n"
        code += f"{tab}{tab}self,\n"
        code += f"{tab}{tab}row_id: int,\n"
        for p in c["properties"]:
            code += f"{tab}{tab}{p["name"]}: {p["type"]},\n"
        code += f"{tab}) -> None:\n"
        code += f"{tab}{tab}if not isinstance(row_id, int):\n"
        code += f"{tab}{tab}{tab}raise TypeError(\"'row_id' is not of type 'int'\")\n"
        for p in c["properties"]:
            code += f"{tab}{tab}if not isinstance({p["name"]}, {p["type"]}):\n"
            code += f'{tab}{tab}{tab}raise TypeError("\'{p["name"]}\' is not of type \'{p["type"]}\'")\n'
        code += f"{tab}{tab}self.row_id: int = row_id\n"
        for p in c["properties"]:
            code += f"{tab}{tab}self.{p["name"]}: {p["type"]} = {p["name"]}\n"
        code += f"\n"

        # __repr__()
        code += f"{tab}def __repr__(self) -> str:\n"
        code += f'{tab}{tab}return f"{{type(self).__name__}}(row_id={{self.row_id}}, {", ".join(f"{p["name"]}={{self.{p["name"]}}}" for p in c["properties"])})"\n'
        code += f"\n"

        # __eq__()
        code += f"{tab}def __eq__(self, other: \"{c["name"]}\") -> bool:\n"
        code += f"{tab}{tab}return all(getattr(self, f.name) == getattr(other, f.name) for f in self.fields)\n"
    return code
