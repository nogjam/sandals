Feature: Sandals
    # In order to make database schema definition easier,
    # As a developer,
    # I want to be able to define Python data classes and corresponding SQLite
    # schemas with plain JSON.

    Scenario: Plain old data
        Given the following JSON schema
            """
            {
                "version-id": "abcdefg",
                "version-sequence": 1,
                "classes": [
                    {
                        "name": "RadioStation",
                        "properties": [
                            {
                                "name": "count",
                                "type": "int"
                            },
                            {
                                "name": "gt_hundo",
                                "type": "bool"
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
        Then we should be able to persist the following RadioStation records using the generated code
            | count | gt_hundo | number | description |
            | 1     | False    | 95.7   | KJR-FM      |
            | 4     | True     | 107.7  | The End     |
            | 5     | True     | 105.3  | Spirit      |
            | 8     | False    | 98.1   | KING-FM     |

    Scenario: Structured data
        Given the following JSON schema
            """
            {
                "version-id": "abcdefg",
                "version-sequence": 1,
                "classes": [
                    {
                        "name": "CastOfCharacters",
                        "properties": [
                            {
                                "name": "monikers",
                                "type": "list[str]"
                            },
                            {
                                "name": "ages",
                                "type": "list[int]"
                            }
                        ]
                    }
                ]
            }
            """
        When we run the generate command
        Then we should be able to persist the following CastOfCharacters records using the generated code
            | monikers       | ages       |
            | bob, joe, fred | 83, 27, 70 |
            | ann, sue, jane | 33, 44, 55 |

    Scenario: Mix of POD and structured data
        Given the following JSON schema
            """
            {
                "version-id": "abcdefg",
                "version-sequence": 1,
                "classes": [
                    {
                        "name": "NumberSequence",
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
        Then we should be able to persist the following NumberSequence records using the generated code
            | title     | integers            |
            | fibonacci | 0, 1, 1, 2, 3, 5, 8 |
            | squares   | 0, 1, 4, 9, 16, 25  |

# Scenario: One-to-many object relationship
#     Given the following JSON schema
#         """
#         {
#             "version-id": "abcdefg",
#             "version-sequence": 1,
#             "classes": [
#                 {
#                     "name": "Item",
#                     "properties": [
#                         {
#                             "name": "name",
#                             "type": "str"
#                         },
#                         {
#                             "name": "price",
#                             "type": "float"
#                         }
#                     ]
#                 },
#                 {
#                     "name": "Box",
#                     "properties": [
#                         {
#                             "name": "color",
#                             "type": "str"
#                         },
#                         {
#                             "name": "n_items",
#                             "type": "int"
#                         },
#                         {
#                             "name": "items",
#                             "type": "list[Item]"
#                         }
#                     ]
#                 }
#             ]
#         }
#         """
#     When we run the generate command
#     Then we should be able to persist the following Box records using the generated code
#         | type | color  | n_items | items              | name   | price |
#         | Box  | red    | 2       | sphere, purse      | --     | --    |
#         | Box  | yellow | 1       | cube, sphere, cube | --     | --    |
#         | Item | --     | --      | --                 | sphere | 12.12 |
#         | Item | --     | --      | --                 | purse  | 55.80 |
#         | Item | --     | --      | --                 | cube   | 6.00  |

# TODO: A scenario with only structured data.

# TODO: A scenario where another custom class is not contained in a list.
