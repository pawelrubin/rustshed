from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import (
    Any,
    Callable,
    Generic,
    NoReturn,
    ParamSpec,
    TypeGuard,
    TypeVar,
    cast,
    overload,
)

from .panic import Panic

T_co = TypeVar("T_co", covariant=True)
E_co = TypeVar("E_co", covariant=True)
U = TypeVar("U")
R = TypeVar("R")
F = TypeVar("F")
P = ParamSpec("P")


class ResultShortcutError(Exception, Generic[E_co]):
    def __init__(self, error: Err[E_co]) -> None:
        super().__init__(
            f"The Q operator used without rustshed.result_shortcut decorator!"
        )
        self.error = error


class OptionShortcutError(Exception):
    ...


class _BaseOption(ABC, Generic[T_co]):
    @abstractmethod
    def is_some(self) -> TypeGuard[Some[T_co]]:
        """
        Returns true if the option is a Some value.
        """

    @abstractmethod
    def is_some_and(self, f: Callable[[T_co], bool]) -> bool:
        """
        Returns true if the option is a Some and the value inside of it matches a predicate.
        """

    @abstractmethod
    def is_null(self) -> TypeGuard[NullType]:
        """
        Returns true if the option is a Null value.
        """

    @abstractmethod
    def expect(self, msg: str) -> T_co:
        """
        Returns the contained Some value, consuming the self value.

        Panics if the value is a Null with a custom panic message provided by msg.
        """

    @abstractmethod
    def unwrap(self) -> T_co:
        """
        Returns the contained Some value, consuming the self value.

        Because this function may panic, its use is generally discouraged.
        Instead, prefer to use pattern matching and handle the Null case explicitly,
        or call unwrap_or, unwrap_or_else, or unwrap_or_default.

        Panics if the self value equals Null.
        """

    @abstractmethod
    def unwrap_or(self, default: T_co) -> T_co:  # type: ignore
        """
        Returns the contained Some value or a provided default.

        Arguments passed to unwrap_or are eagerly evaluated;
        if you are passing the result of a function call,
        it is recommended to use unwrap_or_else, which is lazily evaluated.
        """

    @abstractmethod
    def unwrap_or_else(self, f: Callable[[], T_co]) -> T_co:
        """
        Returns the contained Some value or computes it from a closure.
        """

    @abstractmethod
    def map(self, f: Callable[[T_co], U]) -> Option[U]:
        """
        Maps an Option<T> to Option<U> by applying a function to a contained value.
        """

    @abstractmethod
    def map_or(self, default: U, f: Callable[[T_co], U]) -> U:
        """
        Returns the provided default result (if Null),
        or applies a function to the contained value (if any).

        Arguments passed to map_or are eagerly evaluated;
        if you are passing the result of a function call,
        it is recommended to use map_or_else, which is lazily evaluated.
        """

    @abstractmethod
    def map_or_else(self, default: Callable[[], U], f: Callable[[T_co], U]) -> U:
        """
        Computes a default function result (if null),
        or applies a different function to the contained value (if any).
        """

    @abstractmethod
    def and_(self, optb: Option[U]) -> Option[U]:
        """
        Returns Null if the option is Null, otherwise returns optb.
        """

    @abstractmethod
    def and_then(self, f: Callable[[T_co], Option[U]]) -> Option[U]:
        """
        Returns Null if the option is Null,
        otherwise calls f with the wrapped value and returns the result.

        Some languages call this operation flatmap.

        Often used to chain fallible operations that may return Null.
        """

    @abstractmethod
    def filter(self, predicate: Callable[[T_co], bool]) -> Option[T_co]:
        """
        Returns Null if the option is Null,
        otherwise calls predicate with the wrapped value and returns:

        - Some(t) if predicate returns true (where t is the wrapped value)
        - Null if predicate returns false.

        This function works similar to filter().
        You can imagine the Option<T> being an iterator over one or zero elements.
        filter() lets you decide which elements to keep.
        """

    @abstractmethod
    def or_(self, optb: Option[T_co]) -> Option[T_co]:
        """
        Returns the option if it contains a value, otherwise returns optb.

        Arguments passed to or are eagerly evaluated;
        if you are passing the result of a function call,
        it is recommended to use or_else, which is lazily evaluated.
        """

    @abstractmethod
    def or_else(self, f: Callable[[], Option[T_co]]) -> Option[T_co]:
        """
        Returns the option if it contains a value,
        otherwise calls f and returns the result.
        """

    @abstractmethod
    def xor(self, optb: Option[T_co]) -> Option[T_co]:
        """
        Returns Some if exactly one of self, optb is Some, otherwise returns Null.
        """

    @abstractmethod
    def zip(self, other: Option[U]) -> Option[tuple[T_co, U]]:
        """
        Zips self with another Option.

        If self is Some(s) and other is Some(o),
        this method returns Some((s, o)).
        Otherwise, Null is returned.
        """

    @abstractmethod
    def zip_with(self, other: Option[U], f: Callable[[T_co, U], R]) -> Option[R]:
        """
        Zips self and another Option with function f.

        If self is Some(s) and other is Some(o),
        this method returns Some(f(s, o)).
        Otherwise, Null is returned.
        """

    @abstractmethod
    def unzip(self: _BaseOption[tuple[U, R]]) -> tuple[Option[U], Option[R]]:
        """
        Unzips an option containing a tuple of two options.

        If self is Some((a, b)) this method returns (Some(a), Some(b)).
        Otherwise, (Null, Null) is returned.
        """

    @abstractmethod
    def flatten(self: _BaseOption[_BaseOption[U]]) -> Option[U]:
        """
        Converts from Option<Option<T>> to Option<T>.
        """

    @property
    @abstractmethod
    def Q(self) -> T_co:
        """
        TODO: docs
        """


@dataclass
class Some(_BaseOption[T_co]):
    value: T_co

    def is_some(self) -> TypeGuard[Some[T_co]]:
        return True

    def is_some_and(self, f: Callable[[T_co], bool]) -> bool:
        return f(self.value)

    def is_null(self) -> TypeGuard[NullType]:
        return False

    def expect(self, msg: str) -> T_co:
        return self.value

    def unwrap(self) -> T_co:
        return self.value

    def unwrap_or(self, default: Any) -> T_co:
        return self.value

    def unwrap_or_else(self, f: Callable[[], T_co]) -> T_co:
        return self.value

    def map(self, f: Callable[[T_co], U]) -> Some[U]:
        return Some(f(self.value))

    def map_or(self, default: U, f: Callable[[T_co], U]) -> U:
        return f(self.value)

    def map_or_else(self, default: Callable[[], U], f: Callable[[T_co], U]) -> U:
        return f(self.value)

    def and_(self, optb: Option[U]) -> Option[U]:
        return optb

    def and_then(self, f: Callable[[T_co], Option[U]]) -> Option[U]:
        return f(self.value)

    def filter(self, predicate: Callable[[T_co], bool]) -> Option[T_co]:
        return Some(self.value) if predicate(self.value) else Null

    def or_(self, optb: Option[T_co]) -> Some[T_co]:
        return self

    def or_else(self, f: Callable[[], Option[T_co]]) -> Some[T_co]:
        return self

    def xor(self, optb: Option[T_co]) -> Option[T_co]:
        return self if optb.is_null() else Null

    @overload
    def zip(self, other: NullType) -> NullType:
        ...  # pragma: no cover

    @overload
    def zip(self, other: Some[U]) -> Some[tuple[T_co, U]]:
        ...  # pragma: no cover

    @overload
    def zip(self, other: Option[U]) -> Option[tuple[T_co, U]]:
        ...  # pragma: no cover

    def zip(self, other: Option[U]) -> Option[tuple[T_co, U]]:
        match other:
            case Some(value):
                return Some((self.value, value))
            case _:
                return Null

    @overload
    def zip_with(self, other: NullType, f: Callable[[T_co, Any], Any]) -> NullType:
        ...  # pragma: no cover

    @overload
    def zip_with(self, other: Some[U], f: Callable[[T_co, U], R]) -> Some[R]:
        ...  # pragma: no cover

    @overload
    def zip_with(self, other: Option[U], f: Callable[[T_co, U], R]) -> Option[R]:
        ...  # pragma: no cover

    def zip_with(self, other: Option[U], f: Callable[[T_co, U], R]) -> Option[R]:
        match other:
            case Some(value):
                return Some(f(self.value, value))
            case _:
                return Null

    def unzip(self: _BaseOption[tuple[U, R]]) -> tuple[Option[U], Option[R]]:
        match self:
            case Some((left, right)):
                return cast(tuple[Option[U], Option[R]], (Some(left), Some(right)))
            case _:
                return Null, Null

    @overload
    def flatten(self: Some[NullType]) -> NullType:
        ...  # pragma: no cover

    @overload
    def flatten(self: Some[Some[U]]) -> Some[U]:
        ...  # pragma: no cover

    @overload
    def flatten(self: Some[Option[U]]) -> Option[U]:
        ...  # pragma: no cover

    def flatten(self: Some[Any]) -> Any:
        match self:
            case Some(NullType()):
                return Null
            case Some(Some(val)):
                return Some(val)
            case _:  # pragma: no cover
                # it will never happen
                raise

    @property
    def Q(self) -> T_co:
        return self.value


@dataclass
class NullType(_BaseOption[Any]):
    def is_some(self) -> TypeGuard[Some[Any]]:
        return False

    def is_some_and(self, f: Callable[[Any], bool]) -> bool:
        return False

    def is_null(self) -> TypeGuard[NullType]:
        return True

    def expect(self, msg: str) -> NoReturn:
        raise Panic(msg)

    def unwrap(self) -> NoReturn:
        raise Panic()

    def unwrap_or(self, default: U) -> U:
        return default

    def unwrap_or_else(self, f: Callable[[], T_co]) -> T_co:
        return f()

    def map(self, f: Callable[[Any], Any]) -> NullType:
        return self

    def map_or(self, default: U, f: Callable[[Any], U]) -> U:
        return default

    def map_or_else(self, default: Callable[[], U], f: Callable[[Any], U]) -> U:
        return default()

    def and_(self, optb: Option[Any]) -> NullType:
        return self

    def and_then(self, f: Callable[[Any], Option[U]]) -> NullType:
        return self

    def filter(self, predicate: Callable[[T_co], bool]) -> NullType:
        return self

    def or_(self, optb: Option[T_co]) -> Option[T_co]:
        return optb

    def or_else(self, f: Callable[[], Option[T_co]]) -> Option[T_co]:
        return f()

    @overload
    def xor(self, optb: NullType) -> NullType:
        ...  # pragma: no cover

    @overload
    def xor(self, optb: Some[T_co]) -> Some[T_co]:
        ...  # pragma: no cover

    @overload
    def xor(self, optb: Option[T_co]) -> Option[T_co]:
        ...  # pragma: no cover

    def xor(self, optb: Option[T_co]) -> Option[T_co]:
        return self if optb.is_null() else optb

    def zip(self, other: Option[U]) -> NullType:
        return Null

    def zip_with(self, other: Option[U], f: Callable[[Any, U], Any]) -> NullType:
        return Null

    def unzip(self) -> tuple[NullType, NullType]:
        return (Null, Null)

    def flatten(self: _BaseOption[_BaseOption[Any]]) -> NullType:
        return Null

    @property
    def Q(self) -> NoReturn:
        raise OptionShortcutError


Option = Some[T_co] | NullType

Null = NullType()


def to_option(f: Callable[P, T_co]) -> Callable[P, Option[T_co]]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Option[T_co]:
        try:
            return Some(f(*args, **kwargs))
        except:
            return Null

    return wrapper


class _BaseResult(ABC, Generic[T_co, E_co]):
    @abstractmethod
    def is_ok(self) -> TypeGuard[Ok[T_co]]:
        """
        Returns true if the result is Ok.
        """

    @abstractmethod
    def is_ok_and(self, f: Callable[[T_co], bool]) -> bool:
        """
        Returns true if the result is Ok
        and the value inside of it matches a predicate.
        """

    @abstractmethod
    def is_err(self) -> TypeGuard[Err[E_co]]:
        """
        Returns true if the result is Err.
        """

    @abstractmethod
    def is_err_and(self, f: Callable[[E_co], bool]) -> bool:
        """
        Returns true if the result is Err
        and the value inside of it matches a predicate.
        """

    @abstractmethod
    def ok(self) -> Option[T_co]:
        """
        Converts from Result<T, E> to Option<T>.

        Converts self into an Option<T>, consuming self,
        and discarding the error, if any.
        """

    @abstractmethod
    def err(self) -> Option[E_co]:
        """
        Converts from Result<T, E> to Option<E>.

        Converts self into an Option<E>, consuming self,
        and discarding the success value, if any.
        """

    @abstractmethod
    def map(self, fn: Callable[[T_co], U]) -> Result[U, E_co]:
        """
        Maps a Result<T, E> to Result<U, E>
        by applying a function to a contained Ok value,
        leaving an Err value untouched.

        This function can be used to compose the results of two functions.
        """

    @abstractmethod
    def map_or(self, default: U, fn: Callable[[T_co], U]) -> U:
        """
        Returns the provided default (if Err),
        or applies a function to the contained value (if Ok),

        Arguments passed to map_or are eagerly evaluated;
        if you are passing the result of a function call,
        it is recommended to use map_or_else, which is lazily evaluated.ń
        """

    @abstractmethod
    def map_or_else(self, default: Callable[[E_co], U], fn: Callable[[T_co], U]) -> U:
        """
        Maps a Result<T, E> to U by applying fallback function default
        to a contained Err value, or function f to a contained Ok value.

        This function can be used to unpack a successful result
        while handling an error.
        """

    @abstractmethod
    def map_err(self, op: Callable[[E_co], F]) -> Result[T_co, F]:
        """
        Maps a Result<T, E> to Result<T, F> by applying a function
        to a contained Err value, leaving an Ok value untouched.

        This function can be used to pass through a successful result
        while handling an error.
        """

    @abstractmethod
    def expect(self, msg: str) -> T_co:
        """
        Returns the contained Ok value, consuming the self value.

        Panics if the value is an Err, with a panic message
        including the passed message, and the content of the Err.
        """

    @abstractmethod
    def unwrap(self) -> T_co:
        """
        Returns the contained Ok value, consuming the self value.

        Because this function may panic, its use is generally discouraged.
        Instead, prefer to use pattern matching and handle the Err case explicitly,
        or call unwrap_or, unwrap_or_else, or unwrap_or_default.

        Panics if the value is an Err,
        with a panic message provided by the Err's value.
        """

    @abstractmethod
    def expect_err(self, msg: str) -> E_co:
        """
        Returns the contained Err value, consuming the self value.

        Panics if the value is an Ok, with a panic message
        including the passed message, and the content of the Ok.
        """

    @abstractmethod
    def unwrap_err(self) -> E_co:
        """
        Returns the contained Err value, consuming the self value.

        Panics if the value is an Ok, with a custom panic message
        provided by the Ok's value.
        """

    @abstractmethod
    def and_(self, res: Result[U, E_co]) -> Result[U, E_co]:
        """
        Returns res if the result is Ok, otherwise returns the Err value of self.
        """

    @abstractmethod
    def and_then(self, op: Callable[[T_co], Result[U, E_co]]) -> Result[U, E_co]:
        """
        Calls op if the result is Ok, otherwise returns the Err value of self.

        This function can be used for control flow based on Result values.
        Often used to chain fallible operations that may return Err.
        """

    @abstractmethod
    def or_(self, res: Result[T_co, F]) -> Result[T_co, F]:
        """
        Returns res if the result is Err, otherwise returns the Ok value of self.

        Arguments passed to or are eagerly evaluated;
        if you are passing the result of a function call,
        it is recommended to use or_else, which is lazily evaluated.
        """

    @abstractmethod
    def or_else(self, op: Callable[[E_co], Result[T_co, F]]) -> Result[T_co, F]:
        """
        Calls op if the result is Err, otherwise returns the Ok value of self.

        This function can be used for control flow based on result values.
        """

    @abstractmethod
    def unwrap_or(self, default: T_co) -> T_co:  # type: ignore
        """
        Returns the contained Ok value or a provided default.

        Arguments passed to unwrap_or are eagerly evaluated;
        if you are passing the result of a function call,
        it is recommended to use unwrap_or_else, which is lazily evaluated.
        """

    @abstractmethod
    def unwrap_or_else(self, op: Callable[[E_co], T_co]) -> T_co:
        """
        Returns the contained Ok value or computes it from a closure.
        """

    @abstractmethod
    def contains(self, x: object) -> bool:
        """
        Returns true if the result is an Ok value containing the given value.
        """

    @abstractmethod
    def contains_err(self, f: object) -> bool:
        """
        Returns true if the result is an Err value containing the given value.
        """

    @property
    @abstractmethod
    def Q(self) -> T_co:
        ...


@dataclass
class Ok(_BaseResult[T_co, Any]):
    value: T_co

    def is_ok(self) -> TypeGuard[Ok[T_co]]:
        return True

    def is_ok_and(self, f: Callable[[T_co], bool]) -> bool:
        return f(self.value)

    def is_err(self) -> TypeGuard[Err[Any]]:
        return False

    def is_err_and(self, f: Callable[[Any], bool]) -> bool:
        return False

    def ok(self) -> Some[T_co]:
        return Some(self.value)

    def err(self) -> NullType:
        return Null

    def map(self, fn: Callable[[T_co], U]) -> Ok[U]:
        return Ok(fn(self.value))

    def map_or(self, default: U, fn: Callable[[T_co], U]) -> U:
        return fn(self.value)

    def map_or_else(self, default: Callable[[Any], U], fn: Callable[[T_co], U]) -> U:
        return fn(self.value)

    def map_err(self, op: Callable[[Any], Any]) -> Ok[T_co]:
        return self

    def expect(self, msg: str) -> T_co:
        return self.value

    def unwrap(self) -> T_co:
        return self.value

    def expect_err(self, msg: str) -> NoReturn:
        raise Panic(f"{msg}: {self.value}")

    def unwrap_err(self) -> NoReturn:
        raise Panic(self.value)

    def and_(self, res: Result[U, E_co]) -> Result[U, E_co]:
        return res

    def and_then(self, op: Callable[[T_co], Result[U, E_co]]) -> Result[U, E_co]:
        return op(self.value)

    def or_(self, res: Result[T_co, F]) -> Result[T_co, F]:
        return self

    def or_else(self, op: Callable[[Any], Result[T_co, F]]) -> Result[T_co, F]:
        return self

    def unwrap_or(self, default: Any) -> T_co:
        return self.value

    def unwrap_or_else(self, op: Callable[[Any], T_co]) -> T_co:
        return self.value

    def contains(self, x: object) -> bool:
        return self.value == x

    def contains_err(self, f: Any) -> bool:
        return False

    @property
    def Q(self) -> T_co:
        return self.value


@dataclass
class Err(_BaseResult[Any, E_co]):
    error: E_co

    def is_ok(self) -> TypeGuard[Ok[Any]]:
        return False

    def is_ok_and(self, f: Callable[[Any], bool]) -> bool:
        return False

    def is_err(self) -> TypeGuard[Err[E_co]]:
        return True

    def is_err_and(self, f: Callable[[E_co], bool]) -> bool:
        return f(self.error)

    def ok(self) -> NullType:
        return Null

    def err(self) -> Some[E_co]:
        return Some(self.error)

    def map(self, fn: Callable[[Any], Any]) -> Err[E_co]:
        return self

    def map_or(self, default: U, fn: Callable[[Any], U]) -> U:
        return default

    def map_or_else(self, default: Callable[[E_co], U], fn: Callable[[Any], U]) -> U:
        return default(self.error)

    def map_err(self, op: Callable[[E_co], F]) -> Err[F]:
        return Err(op(self.error))

    def expect(self, msg: str) -> NoReturn:
        raise Panic(msg)

    def unwrap(self) -> NoReturn:
        raise Panic(self.error)

    def expect_err(self, msg: str) -> E_co:
        return self.error

    def unwrap_err(self) -> E_co:
        return self.error

    def and_(self, res: Result[Any, Any]) -> Err[E_co]:
        return self

    def and_then(self, op: Callable[[Any], Result[Any, Any]]) -> Err[E_co]:
        return self

    def or_(self, res: Result[T_co, F]) -> Result[T_co, F]:
        return res

    def or_else(self, op: Callable[[E_co], Result[T_co, F]]) -> Result[T_co, F]:
        return op(self.error)

    def unwrap_or(self, default: U) -> U:
        return default

    def unwrap_or_else(self, op: Callable[[E_co], T_co]) -> T_co:
        return op(self.error)

    def contains(self, x: Any) -> bool:
        return False

    def contains_err(self, f: object) -> bool:
        return self.error == f

    @property
    def Q(self) -> NoReturn:
        raise ResultShortcutError(self)


Result = Ok[T_co] | Err[E_co]


E_rr = TypeVar("E_rr", bound=Exception)


class to_result_type:
    def __call__(self, f: Callable[P, T_co]) -> Callable[P, Result[T_co, Exception]]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T_co, Exception]:
            try:
                return Ok(f(*args, **kwargs))
            except Exception as err:
                return Err(err)

        return wrapper

    def __getitem__(
        self, _: type[E_rr]
    ) -> Callable[[Callable[P, T_co]], Callable[P, Result[T_co, E_rr]]]:
        return self  # type: ignore


to_result = to_result_type()

IOResult = Result[T_co, IOError]

RT = TypeVar("RT")


def result_shortcut(
    f: Callable[P, Result[T_co, E_co]]
) -> Callable[P, Result[T_co, E_co]]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T_co, E_co]:
        try:
            return f(*args, **kwargs)
        except ResultShortcutError as err:
            return cast(Result[T_co, E_co], err.error)

    return wrapper


def option_shortcut(f: Callable[P, Option[T_co]]) -> Callable[P, Option[T_co]]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Option[T_co]:
        try:
            return f(*args, **kwargs)
        except OptionShortcutError:
            return cast(Option[T_co], Null)

    return wrapper
