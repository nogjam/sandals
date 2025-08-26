"""Core functionality of sandals."""

from sandals import config


tab: str = " " * 2
type_map: dict[str, str] = {"int": "INTEGER", "str": "TEXT"}


def generate_sql_schema_from_json_data(data: dict) -> str:
    schema: str = ""
    for table in data["tables"]:
        schema += f"\nCREATE TABLE IF NOT EXISTS {table['name']} (\n"
        schema += f"{tab}row_id INTEGER PRIMARY KEY,\n"
        for col in table["columns"]:
            schema += f"{tab}{col['name']} {type_map[col['type']]} NOT NULL,\n"
        schema = schema.rstrip(",\n") + "\n"
        schema += ")\n"
    return schema


def generate_python_from_json_data(data: dict) -> str:
    with open(config.TEMPLATE_PATH, "r") as f:
        template: str = f.read()

    template.replace(
        f"# {config.TEMPLATE_LOC_GENERATED_CLASSES}", _generate_dataclass_code(data)
    )
    return template


def _generate_dataclass_code(data: dict) -> str:
    code: str = ""
    tab: str = " " * 4
    for c in data["classes"]:
        # TODO: Remove AI creativity.
        code += f"class {c['name'].capitalize()}(DataClass):\n"
        code += f"{tab}table_name: str = '{c['name']}'\n"
        fields = [col["name"] for col in c["columns"]]
        code += f"{tab}_fields: list[str] = {fields}\n\n"
        code += f"{tab}def __init__(self, "
        init_params = [f"{col['name']}: {col['type']}" for col in c["columns"]]
        code += ", ".join(init_params) + ") -> None:\n"
        for col in c["columns"]:
            code += f"{tab*2}self.{col['name']}: {col['type']} = {col['name']}\n"
        code += "\n\n"
        code += f"def insert_{c['name']}(conn: sqlite3.Connection, {c['name']}: {c['name'].capitalize()}) -> None:\n"
        code += f"{tab}placeholders = ', '.join('?' * len({c['name']}._fields))\n"
        code += f"{tab}columns = ', '.join({c['name']}._fields)\n"
        code += f"{tab}sql = f'INSERT INTO {c['name']} ({{columns}}) VALUES ({{placeholders}})'\n"
        code += f"{tab}conn.execute(sql, {c['name']}.marshall_values())\n"
        code += f"{tab}conn.commit()\n\n\n"
    return code
