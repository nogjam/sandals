"""Utilities for various purposes."""

def pascal_case_to_snake_case(s: str) -> str:
    result: str = ""
    cap_a: int = ord("A")
    cap_z: int = ord("Z")
    first: bool = True
    for char in s:
        if (d := ord(char)) >= cap_a and d <= cap_z:
            if not first:
                result += "_"
            result += char.lower()
        else:
            result += char
        first = False
    return result
