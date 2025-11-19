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

    Scenario: One-to-many plain ol' data relationship
        Given the following JSON schema
            """
            {
                "version-id": "abcdefg",
                "version-sequence": 1,
                "classes": [
                    {
                        "name": "PodOneToMany",
                        "properties": [
                            {
                                "name": "title",
                                "type": "str"
                            },
                            {
                                "name": "integers",
                                "type": "list[int]"
                            }
                        ]
                    }
                ]
            }
            """
        When we run the generate command
        Then we should be able to persist the following records using the generated code
            | title     | integers              |
            | fibonacci | [0, 1, 1, 2, 3, 5, 8] |
            | squares   | [0, 1, 4, 9, 16, 25]  |

    Scenario: One-to-many object relationship
        Given the following JSON schema
            """
            {
                "version-id": "abcdefg",
                "version-sequence": 1,
                "classes": [
                    {
                        "name": "Box",
                        "properties": [
                            {
                                "name": "color",
                                "type": "str"
                            },
                            {
                                "name": "n_items",
                                "type": "int"
                            },
                            {
                                "name": "items",
                                "type": "list[Item]"
                            }
                        ]
                    },
                    {
                        "name": "Item",
                        "properties": [
                            {
                                "name": "name",
                                "type": "str"
                            },
                            {
                                "name": "price",
                                "type": "float"
                            }
                        ]
                    }
                ]
            }
            """
        When we run the generate command
        Then we should be able to persist the following records using the generated code
            | type | color  | n_items | items         | name   | price |
            | Box  | red    | 2       | sphere, purse | --     | --    |
            | Item | --     | --      | --            | sphere | 12.12 |
            | Item | --     | --      | --            | purse  | 55.80 |
            | Box  | yellow | 1       | cube          | --     | --    |
            | Item | --     | --      | --            | cube   | 6.00  |
