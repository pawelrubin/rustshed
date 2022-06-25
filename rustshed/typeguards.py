from typing import Any, TypeGuard, TypeVar

from rustshed.option_result import Err, NullType, Ok, Option, Result, Some

T = TypeVar("T")
E = TypeVar("E")


def is_some(opt: Option[T]) -> TypeGuard[Some[T]]:
    return opt.is_some()


def is_null(opt: Option[Any]) -> TypeGuard[NullType]:
    return opt.is_null()


def is_ok(res: Result[T, Any]) -> TypeGuard[Ok[T]]:
    return res.is_ok()


def is_err(res: Result[Any, E]) -> TypeGuard[Err[E]]:
    return res.is_err()
