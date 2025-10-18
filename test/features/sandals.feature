Feature: Sandals
    # In order to make database schema definition easier,
    # As a developer,
    # I want to be able to define Python data classes and corresponding SQLite
    # schemas with plain JSON.

    Scenario: Simple schema
        Given the following JSON schema
            """
            {
                "version-id": "abcdefg",
                "version-sequence": 1,
                "classes": [
                    {
                        "name": "SimpleData",
                        "properties": [
                            {
                                "name": "count",
                                "type": "int"
                            },
                            {
                                "name": "number",
                                "type": "float"
                            },
                            {
                                "name": "description",
                                "type": "str"
                            }
                        ]
                    }
                ]
            }
            """
        When we run the generate command
        Then the following SQL should be generated
            """
            CREATE TABLE IF NOT EXISTS simple_data (
              row_id INTEGER PRIMARY KEY,
              count INTEGER NOT NULL,
              number REAL NOT NULL,
              description TEXT NOT NULL
            )
            """
        And we should be able to persist a record using the generated Python code
