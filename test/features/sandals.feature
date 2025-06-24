Feature: Sandals
    # In order to make database schema definition easier,
    # As a developer,
    # I want to be able to define a schema with plain JSON.

    Scenario: Simple schema
        Given the following JSON schema
            """
            {
                "version-id": "abcdefg",
                "version-sequence": 1,
                "tables": [
                    {
                        "name": "bob",
                        "columns": [
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
        And we should be able to persist the following records
            """
            [
                (1, "The first"),
                (2, "The second"),
            ]
            """
