from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from rustshed.option_result import Null, Option, Some

T = TypeVar("T")
P = ParamSpec("P")


def to_option(f: Callable[P, T]) -> Callable[P, Option[T]]:
    """
    Converts a callable that returns `T` to a callable that returns `Option[T]`

    ### Example
    ```
    from rustshed import to_option


    @to_option
    def parse(s: str) -> int:
        return int(s)

    # when run with mypy or pyright
    reveal_type(parse("1"))  # Option[int]
    """

    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return Some(f(*args, **kwargs))
        except Exception:  # pylint: disable=broad-except
            return Null

    return wrapper
