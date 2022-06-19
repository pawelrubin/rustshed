from typing import TypeVar

from examples.shared import ParseIntError, parse
from rustshed import Err, Ok, Result

T = TypeVar("T")

# Define a generic alias for a `Result` with the error type `ParseIntError`.
AliasedResult = Result[T, ParseIntError]


# Use the above alias to refer to our specific `Result` type.
def multiply(first_number_str: str, second_number_str: str) -> AliasedResult[int]:
    return parse(first_number_str).and_then(
        lambda first_number: parse(second_number_str).map(
            lambda second_number: first_number * second_number
        )
    )


def print_result(result: Result[int, ParseIntError]) -> None:
    match result:
        case Ok(n):
            print(f"n is {n}")
        case Err(e):
            print(f"Error: {e}")


def main() -> None:
    print_result(multiply("10", "2"))
    print_result(multiply("t", "2"))


if __name__ == "__main__":
    main()
