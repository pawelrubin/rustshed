from examples.shared import ParseIntError, parse
from rustshed import Err, Ok, Result


def multiply(
    first_number_str: str, second_number_str: str
) -> Result[int, ParseIntError]:
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
    # This still presents a reasonable answer.
    twenty = multiply("10", "2")
    print_result(twenty)

    # The following now provides a much more helpful error message.
    tt = multiply("t", "2")
    print_result(tt)


if __name__ == "__main__":
    main()
