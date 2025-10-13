"""Core functionality of sandals."""

from sandals import config
from sandals.util import pascal_case_to_snake_case


tab: str = " " * 2
type_map: dict[str, str] = {"int": "INTEGER", "float": "REAL", "str": "TEXT"}


def generate_sql_schema_from_json_data(data: dict) -> str:
    k_classes: str = "classes"
    k_name: str = "name"
    k_properties: str = "properties"
    k_prop_name: str = "name"
    k_prop_type: str = "type"
    schema: str = ""
    for class_ in data[k_classes]:
        schema += f"\nCREATE TABLE IF NOT EXISTS {class_[k_name]} (\n"
        schema += f"{tab}row_id INTEGER PRIMARY KEY,\n"
        for prop in class_[k_properties]:
            schema += (
                f"{tab}{prop[k_prop_name]} {type_map[prop[k_prop_type]]} NOT NULL,\n"
            )
        schema = schema.rstrip(",\n") + "\n"
        schema += ")\n"
    return schema


def generate_python_from_json_data(data: dict) -> str:
    with open(config.TEMPLATE_PATH, "r") as f:
        template: str = f.read()

    return template.replace(
        f"# {config.TEMPLATE_LOC_GENERATED_CLASSES}", _generate_dataclass_code(data)
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
        code += f'{tab}table_name: str = "{pascal_case_to_snake_case(c["name"])}"\n'
        code += f"{tab}fields: list[Field] = [\n"
        for p in c["properties"]:
            code += (
                f'{tab}{tab}Field("{p["name"]}", "{SQLITE_TYPE_MAPPING[p["type"]]}"),\n'
            )
        code += f"{tab}]\n"
        code += f"\n"
        code += f"{tab}def __init__(\n"
        code += f"{tab}{tab}self,\n"
        for p in c["properties"]:
            code += f"{tab}{tab}{p["name"]}: {p["type"]},\n"
        code += f"{tab}) -> None:\n"
        for p in c["properties"]:
            code += f"{tab}{tab}if not isinstance({p["name"]}, {p["type"]}):\n"
            code += f'{tab}{tab}{tab}raise TypeError("\'{p["name"]}\' is not of type \'{p["type"]}\'")\n'
        for p in c["properties"]:
            code += f"{tab}{tab}self.{p["name"]}: {p["type"]} = {p["name"]}\n"
    return code
