tab: str = " " * 2
type_map: dict[str, str] = {"int": "INTEGER", "str": "TEXT"}


def generate_sql_schema_from_json_data(data: dict) -> str:
    schema: str = ""
    for table in data["tables"]:
        schema += f"\nCREATE TABLE IF NOT EXISTS {table['name']} ("
        schema += f"{tab}row_id INTEGER PRIMARY KEY,"
        for col in table["columns"]:
            schema += f"{tab}{col['name']} {type_map[col['type']]} NOT NULL,\n"
        schema.rstrip(",\n")
        schema += ")\n"
    return schema
