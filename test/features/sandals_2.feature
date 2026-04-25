Feature: Sandals
    # In order to make database schema definition easier,
    # As a developer,
    # I want to be able to define Python data classes and corresponding SQLite
    # schemas with Python class templates.

    Scenario: Plain old data
        Given the following metadata and class templates in module pod
            """
            {
                "version-id": "abcdefg",
                "version-sequence": 1,
                "classes": [
                    "RadioStation"
                ]
            }
            """
        When we run the generate command 2
        Then we should be able to persist the following RadioStation records using the generated code 2
            | count | gt_hundo | number | description |
            | 1     | False    | 95.7   | KJR-FM      |
            | 4     | True     | 107.7  | The End     |
            | 5     | True     | 105.3  | Spirit      |
            | 8     | False    | 98.1   | KING-FM     |
