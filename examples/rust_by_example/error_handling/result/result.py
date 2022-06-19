from examples.shared import ParseIntError, parse
from rustshed import Err, Ok, Result


def multiply(first_number_str: str, second_number_str: str) -> int:
    # let's try using `unwrap()` to get the number out. Will it bite us?
    first_number = parse(first_number_str).unwrap()
    second_number = parse(second_number_str).unwrap()
    return first_number * second_number


def main() -> None:
    twenty = multiply("10", "2")
    print(f"double is {twenty}")

    tt = multiply("t", "2")
    print(f"double is {tt}")


def main2() -> Result[tuple[()], ParseIntError]:
    number_str = "10"
    match parse(number_str):
        case Ok(value):
            number = value
        case Err(err):
            return Err(err)
    print(number)
    return Ok(())


if __name__ == "__main__":
    main2()
