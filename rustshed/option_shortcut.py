from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from rustshed.option_result import Null, Option, OptionShortcutError

T = TypeVar("T")
P = ParamSpec("P")


def option_shortcut(f: Callable[P, Option[T]]) -> Callable[P, Option[T]]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return f(*args, **kwargs)
        except OptionShortcutError:
            return Null

    return wrapper
