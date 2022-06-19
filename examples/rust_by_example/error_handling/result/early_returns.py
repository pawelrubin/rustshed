from rustshed import Result, Ok, Err

from examples.shared import ParseIntError, parse


def multiply(
    first_number_str: str, second_number_str: str
) -> Result[int, ParseIntError]:
    match parse(first_number_str):
        case Ok(value):
            first_number = value
        case Err(e):
            return Err(e)

    match parse(second_number_str):
        case Ok(value):
            second_number = value
        case Err(e):
            return Err(e)

    return Ok(first_number * second_number)


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
