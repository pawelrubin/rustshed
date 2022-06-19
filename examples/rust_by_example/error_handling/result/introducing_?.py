from examples.shared import ParseIntError, parse
from rustshed import Err, Ok, Result
from rustshed.option_result import result_shortcut


@result_shortcut
def multiply(
    first_number_str: str, seconds_number_str: str
) -> Result[int, ParseIntError]:
    first_number = parse(first_number_str).Q
    seconds_number = parse(seconds_number_str).Q
    return Ok(first_number * seconds_number)


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
