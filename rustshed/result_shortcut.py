from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from rustshed.option_result import Result, ResultShortcutError

T_co = TypeVar("T_co")
E_co = TypeVar("E_co")
P = ParamSpec("P")


def result_shortcut(
    f: Callable[P, Result[T_co, E_co]]
) -> Callable[P, Result[T_co, E_co]]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T_co, E_co]:
        try:
            return f(*args, **kwargs)
        except ResultShortcutError[E_co] as err:
            return err.error

    return wrapper
