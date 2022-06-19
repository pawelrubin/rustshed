from examples.shared import ParseIntError, parse
from rustshed import Err, Ok, Result


def main() -> Result[None, ParseIntError]:
    number_str = "10"
    match parse(number_str):
        case Ok(value):
            number = value
        case Err(err):
            return Err(err)
    print(number)
    return Ok(None)


if __name__ == "__main__":
    main()
