Feature: Sandals
    # In order to make database schema definition easier,
    # As a developer,
    # I want to be able to define Python data classes and corresponding SQLite
    # schemas with Python class templates.

    Scenario: Plain old data
        Given metadata and class definitions in module test.templates.pod
        When we run the generate command
        Then we should be able to persist the following RadioStation records using the generated code
            | count | gt_hundo | number | description |
            | 1     | False    | 95.7   | KJR-FM      |
            | 4     | True     | 107.7  | The End     |
            | 5     | True     | 105.3  | Spirit      |
            | 8     | False    | 98.1   | KING-FM     |

    Scenario: Structured data
        Given metadata and class definitions in module test.templates.structured
        When we run the generate command
        Then we should be able to persist the following CastOfCharacters records using the generated code
            | monikers       | ages       |
            | bob, joe, fred | 83, 27, 70 |
            | ann, sue, jane | 33, 44, 55 |

    Scenario: Mix of POD and structured data
        Given metadata and class definitions in module test.templates.mix_pod_structured
        When we run the generate command
        Then we should be able to persist the following NumberSequence records using the generated code
            | title     | integers            |
            | fibonacci | 0, 1, 1, 2, 3, 5, 8 |
            | squares   | 0, 1, 4, 9, 16, 25  |

    Scenario: Nested data-class data
        Given metadata and class definitions in module test.templates.nested
        When we run the generate command
        Then we should be able to persist the following Tree records using the generated code
            | type  | name     | color  | classification | fruit    |
            | Fruit | fig      | purple | --             | --       |
            | Fruit | pine nut | brown  | --             | --       |
            | Tree  | --       | --     | deciduous      | fig      |
            | Tree  | --       | --     | evergreen      | pine nut |

    Scenario: Data-class and compound data
        Given metadata and class definitions in module test.templates.dc_and_compound
        When we run the generate command
        Then we should be able to persist the following Box records using the generated code
            | type  | color  | shape  | items                  | name   | price | n_sides |
            | Box   | red    | square | slinky, gem            | --     | --    | --      |
            | Box   | yellow | circle | marble, slinky, marble | --     | --    | --      |
            | Item  | --     | --     | --                     | slinky | 12.12 | --      |
            | Item  | --     | --     | --                     | gem    | 55.80 | --      |
            | Item  | --     | --     | --                     | marble | 6.00  | --      |
            | Shape | --     | --     | --                     | circle | --    | 1       |
            | Shape | --     | --     | --                     | square | --    | 4       |

    Scenario: DataClass with other members
        Given metadata and class definitions in module test.templates.other_members
        When we run the generate command
        Then we should be able to persist the following Money records using the generated code
            | milliunits | dollars | cents | repr  | get_deposit_str |
            | 9034       | 9       | 3     | $9.03 | Deposit $9.03   |
            | 101        | 0       | 10    | $0.10 | Deposit $0.10   |
        And we should be able to use the Money class' methods

# TODO: Scenario with nested data-class/compound data
