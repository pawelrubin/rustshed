from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from rustshed.option_result import Err, Ok, Result

T = TypeVar("T")
E = TypeVar("E", bound=Exception)
P = ParamSpec("P")


class _to_result_type:
    """
    Converts a callable that returns `T` to a callable that returns `Result[T, E]`
    where `E` a subclass of `Exception`.


    ### Example
    ```
    from typing import SupportsIndex, TypeVar

    from rustshed import to_result

    T = TypeVar("T")


    @to_result[IndexError]
    def get_from_lst(lst: list[T], index: SupportsIndex) -> T:
        return lst[index]

    # when run with mypy or pyright
    reveal_type(get_from_lst([1, 2, 3], 3))  # Result[int, IndexError]
    """

    def __call__(self, f: Callable[P, T]) -> Callable[P, Result[T, Exception]]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, Exception]:
            try:
                return Ok(f(*args, **kwargs))
            except Exception as err:  # pylint: disable=broad-except
                return Err(err)

        return wrapper

    def __getitem__(
        self, _: type[E]
    ) -> Callable[[Callable[P, T]], Callable[P, Result[T, E]]]:
        """
        This effectively enables generic type application
        for objects of this callable class
        """
        return self  # type: ignore


to_result = _to_result_type()
to_io_result = to_result[IOError]
