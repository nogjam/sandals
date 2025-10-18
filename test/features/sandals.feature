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
        Then we should be able to persist the following records using the generated code
            | count | number | description |
            | 1     | 95.7   | KJR-FM      |
            | 4     | 107.7  | The End     |
            | 5     | 105.3  | Spirit      |
            | 8     | 98.1   | KING-FM     |
