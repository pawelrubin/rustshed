from rustshed import Result, Ok, Err


from examples.shared import parse, ParseIntError


def multiply(
    first_number_str: str, second_number_str: str
) -> Result[int, ParseIntError]:
    match parse(first_number_str):
        case Ok(first_number):
            match parse(second_number_str):
                case Ok(second_number):
                    result = Ok(first_number * second_number)
                case Err(e):
                    return Err(e)
        case Err(e):
            return Err(e)

    return result


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
