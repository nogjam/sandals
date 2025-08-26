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
                        "name": "Data",
                        "properties": [
                            {
                                "name": "number",
                                "type": "int"
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
            CREATE TABLE IF NOT EXISTS data (
              row_id INTEGER PRIMARY KEY,
              number INTEGER NOT NULL,
              description TEXT NOT NULL
            )
            """
        And we should be able to persist a record using the generated Python code
