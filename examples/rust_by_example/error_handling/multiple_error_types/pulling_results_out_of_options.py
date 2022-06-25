from typing import TypeVar

from examples.shared import ParseIntError, parse
from rustshed import Null, Ok, Option, Result, Some, to_option

T = TypeVar("T")


@to_option
def first(lst: list[T]) -> T:
    return lst.pop(0)


def double_first(lst: list[str]) -> Result[Option[int], ParseIntError]:
    opt = first(lst).map(lambda first: parse(first).map(lambda n: 2 * n))

    return opt.map_or(Ok(Null), lambda r: r.map(Some[int]))  # type: ignore

    # the above is correct and throws no error with pyright,
    #
    # however mypy requires explicit type annotations:
    #
    # default: Result[Option[int], ParseIntError] = Ok(Null)
    # mapper: Callable[
    #     [Result[int, ParseIntError]], Result[Option[int], ParseIntError]
    # ] = lambda r: r.map(Some[int])

    # return opt.map_or(default, mapper)


if __name__ == "__main__":
    numbers = ["42", "93", "18"]
    empty: list[str] = []
    strings = ["tofu", "93", "18"]

    print(f"The first doubled is {double_first(numbers)}")
    print(f"The first doubled is {double_first(empty)}")
    print(f"The first doubled is {double_first(strings)}")
