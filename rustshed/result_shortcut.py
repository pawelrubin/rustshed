from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from rustshed.option_result import Result, ResultShortcutError

T = TypeVar("T")
E = TypeVar("E")
P = ParamSpec("P")


def result_shortcut(f: Callable[P, Result[T, E]]) -> Callable[P, Result[T, E]]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
        try:
            return f(*args, **kwargs)
        except ResultShortcutError[E] as err:
            return err.error

    return wrapper
