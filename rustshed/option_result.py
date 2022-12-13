from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, NoReturn, TypeVar, cast, overload

from .panic import Panic

T_co = TypeVar("T_co", covariant=True)
E_co = TypeVar("E_co", covariant=True)
T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")
R = TypeVar("R")
F = TypeVar("F")


class ResultShortcutError(Exception, Generic[E_co]):
    def __init__(self, error: Err[E_co]) -> None:
        super().__init__(
            "The Q operator used without rustshed.result_shortcut decorator!"
        )
        self.error = error

    def __class_getitem__(cls, item: Any) -> type[ResultShortcutError[E_co]]:
        # enables applying a type parameter for generic Exception class
        # except ResultShortcutError[E] as err:
        return cls


class OptionShortcutError(Exception):
    ...


class _BaseOption(ABC, Generic[T_co]):
    """
    Optional values.

    The Option type represents an optional value: every `Option[T]` is either `Some[T]`
    and contains a value of type `T`, or `Null` (`None` in Rust), and does not.

    ### Example

    Options are commonly paired with pattern matching
    to query the presence of a value and take action,
    always accounting for the Null case.

    ```
    def divide(numerator: float, denominator: float) -> Option[float]:
        if denominator == 0.0:
            return Null
        return Some(numerator / denominator)

    match divide(2.0, 3.0):
        case Some(value):
            print(f"Result: {value}")
        case Null:
            print("Cannot divide by 0)
    ```
    """

    @abstractmethod
    def is_some(self) -> bool:
        """
        Returns true if the option is a Some value.

        Note that this method does not return a TypeGuard.
        This is impossible as per design of PEP-647 TypeGuards.

        If you want to take advantage of a type guard, use `rustshed.is_some` instead.
        """

    @abstractmethod
    def is_some_and(self, f: Callable[[T_co], bool]) -> bool:
        """
        Returns true if the option is a Some and the value inside
        of it matches a predicate.
        """

    @abstractmethod
    def is_null(self) -> bool:
        """
        Returns true if the option is a Null value.

        Note that this method does not return a TypeGuard.
        This is impossible as per design of PEP-647 TypeGuards.

        If you want to take advantage of a type guard, use `rustshed.is_null` instead.
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
    def inspect(self, f: Callable[[T_co], Any]) -> Option[T_co]:
        """
        Calls the provided closure with a reference to the contained value (if Some).
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
    def ok_or(self, err: E) -> Result[T_co, E]:
        """
        Transforms the Option<T> into a Result<T, E>,
        mapping Some(v) to Ok(v) and Null to Err(err).

        Arguments passed to ok_or are eagerly evaluated;
        if you are passing the result of a function call,
        it is recommended to use ok_or_else, which is lazily evaluated.
        """

    @abstractmethod
    def ok_or_else(self, err: Callable[[], E]) -> Result[T_co, E]:
        """
        Transforms the Option<T> into a Result<T, E>,
        mapping Some(v) to Ok(v) and Null to Err(err()).
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
    def transpose(self: _BaseOption[_BaseResult[T, E]]) -> Result[Option[T], E]:
        """
        Transposes an Option of a Result into a Result of an Option.

        Null will be mapped to Ok(Null).
        Some(Ok(T)) and Some(Err(E)) will be mapped to Ok(Some(T)) and Err(E).
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


@dataclass(frozen=True, slots=True)
class Some(_BaseOption[T_co]):
    value: T_co

    def is_some(self) -> bool:
        return True

    def is_some_and(self, f: Callable[[T_co], bool]) -> bool:
        return f(self.value)

    def is_null(self) -> bool:
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

    def inspect(self, f: Callable[[T_co], Any]) -> Option[T_co]:
        f(self.value)
        return self

    def map_or(self, default: U, f: Callable[[T_co], U]) -> U:
        return f(self.value)

    def map_or_else(self, default: Callable[[], U], f: Callable[[T_co], U]) -> U:
        return f(self.value)

    def ok_or(self, err: Any) -> Ok[T_co]:
        return Ok(self.value)

    def ok_or_else(self, err: Any) -> Ok[T_co]:
        return Ok(self.value)

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
    def transpose(self: Some[Ok[T]]) -> Ok[Some[T]]:
        ...  # pragma: no cover

    @overload
    def transpose(self: Some[Err[E]]) -> Err[E]:
        ...  # pragma: no cover

    @overload
    def transpose(self: Option[Result[T, E]]) -> Result[Option[T], E]:
        ...  # pragma: no cover

    def transpose(self: Option[Result[T, E]]) -> Result[Option[T], E]:
        match self:
            case Some(Ok(value)):
                return Ok(Some(value))
            case Some(Err(error)):
                return Err(error)
            case _:  # pragma: no cover
                # it will never happen
                raise RuntimeError

    @overload
    def flatten(self: Some[NullType]) -> NullType:
        ...  # pragma: no cover

    @overload
    def flatten(self: Some[Some[U]]) -> Some[U]:
        ...  # pragma: no cover

    @overload
    def flatten(self: Some[Option[U]]) -> Option[U]:
        ...  # pragma: no cover

    def flatten(self: Some[NullType | Some[U]]) -> NullType | Some[U]:
        match self:
            case Some(NullType()):
                return Null
            case Some(Some(val)):
                return Some(val)
            case _:  # pragma: no cover
                # it will never happen
                raise RuntimeError

    @property
    def Q(self) -> T_co:
        return self.value


@dataclass(frozen=True, slots=True)
class NullType(_BaseOption[Any]):
    def __str__(self) -> str:
        return "Null"

    def is_some(self) -> bool:
        return False

    def is_some_and(self, f: Callable[[Any], bool]) -> bool:
        return False

    def is_null(self) -> bool:
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

    def inspect(self, f: Callable[[Any], Any]) -> NullType:
        return self

    def map_or(self, default: U, f: Callable[[Any], U]) -> U:
        return default

    def map_or_else(self, default: Callable[[], U], f: Callable[[Any], U]) -> U:
        return default()

    def ok_or(self, err: E) -> Result[T_co, E]:
        return Err(err)

    def ok_or_else(self, err: Callable[[], E]) -> Result[T_co, E]:
        return Err(err())

    def and_(self, optb: Option[Any]) -> NullType:
        return self

    def and_then(self, f: Callable[[Any], Option[U]]) -> NullType:
        return self

    def filter(self, predicate: Callable[[Any], bool]) -> NullType:
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

    def transpose(self: _BaseOption[Result[T, E]]) -> Result[NullType, E]:
        return Ok(Null)

    def flatten(self: _BaseOption[_BaseOption[Any]]) -> NullType:
        return Null

    @property
    def Q(self) -> NoReturn:
        raise OptionShortcutError


Option = Some[T_co] | NullType

Null = NullType()


class _BaseResult(ABC, Generic[T_co, E_co]):
    @abstractmethod
    def is_ok(self) -> bool:
        """
        Returns true if the result is Ok.

        Note that this method does not return a TypeGuard.
        This is impossible as per design of PEP-647 TypeGuards.

        If you want to take advantage of a type guard, use `rustshed.is_ok` instead.
        """

    @abstractmethod
    def is_ok_and(self, f: Callable[[T_co], bool]) -> bool:
        """
        Returns true if the result is Ok
        and the value inside of it matches a predicate.
        """

    @abstractmethod
    def is_err(self) -> bool:
        """
        Returns true if the result is Err.

        Note that this method does not return a TypeGuard.
        This is impossible as per design of PEP-647 TypeGuards.

        If you want to take advantage of a type guard, use `rustshed.is_err` instead.
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
    def map_or_else(self, default: Callable[[E_co], U], f: Callable[[T_co], U]) -> U:
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
    def inspect(self, f: Callable[[T_co], Any]) -> Result[T_co, E_co]:
        """
        Calls the provided closure with a reference to the contained value (if Ok).
        """

    @abstractmethod
    def inspect_err(self, f: Callable[[E_co], Any]) -> Result[T_co, E_co]:
        """
        Calls the provided closure with a reference to the contained error (if Err).
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

    @abstractmethod
    def transpose(self: _BaseResult[_BaseOption[T], E]) -> Option[Result[T, E]]:
        """
        Transposes a Result of an Option into an Option of a Result.

        Ok(Null) will be mapped to Null.
        Ok(Some(T)) and Err(E) will be mapped to Some(Ok(T)) and Some(Err(E)).
        """

    @property
    @abstractmethod
    def Q(self) -> T_co:
        ...  # pragma: no cover


@dataclass(frozen=True, slots=True)
class Ok(_BaseResult[T_co, Any]):
    value: T_co

    def is_ok(self) -> bool:
        return True

    def is_ok_and(self, f: Callable[[T_co], bool]) -> bool:
        return f(self.value)

    def is_err(self) -> bool:
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

    def map_or_else(self, default: Callable[[object], U], f: Callable[[T_co], U]) -> U:
        return f(self.value)

    def map_err(self, op: Callable[[Any], Any]) -> Ok[T_co]:
        return self

    def inspect(self, f: Callable[[T_co], Any]) -> Ok[T_co]:
        f(self.value)
        return self

    def inspect_err(self, f: Callable[[Any], Any]) -> Result[T_co, E_co]:
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

    @overload
    def transpose(self: Ok[Some[T]]) -> Some[Ok[T]]:
        ...  # pragma: no cover

    @overload
    def transpose(self: Ok[NullType]) -> NullType:
        ...  # pragma: no cover

    @overload
    def transpose(self: Ok[Option[T]]) -> Option[Ok[T]]:
        ...  # pragma: no cover

    def transpose(self: Ok[Option[T]]) -> Option[Ok[T]]:
        match self:
            case Ok(Some(value)):
                return Some(Ok(value))
            case Ok(NullType()):
                return Null
            case _:  # pragma: no cover
                # it will never happen
                raise RuntimeError

    @property
    def Q(self) -> T_co:
        return self.value


@dataclass(frozen=True, slots=True)
class Err(_BaseResult[Any, E_co]):
    error: E_co

    def is_ok(self) -> bool:
        return False

    def is_ok_and(self, f: Callable[[Any], bool]) -> bool:
        return False

    def is_err(self) -> bool:
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

    def map_or_else(self, default: Callable[[E_co], U], f: Callable[[Any], U]) -> U:
        return default(self.error)

    def map_err(self, op: Callable[[E_co], F]) -> Err[F]:
        return Err(op(self.error))

    def inspect(self, f: Callable[[Any], Any]) -> Err[E_co]:
        return self

    def inspect_err(self, f: Callable[[E_co], Any]) -> Err[E_co]:
        f(self.error)
        return self

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

    def transpose(self: Err[E]) -> Some[Err[E]]:
        return Some(self)

    @property
    def Q(self) -> NoReturn:
        raise ResultShortcutError(self)


Result = Ok[T_co] | Err[E_co]
IOResult = Result[T_co, IOError]
