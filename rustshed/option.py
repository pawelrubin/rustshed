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

T = TypeVar("T")
U = TypeVar("U")
R = TypeVar("R")


class _BaseOption(ABC, Generic[T]):
    @abstractmethod
    def is_some(self) -> TypeGuard[Some[T]]:
        """
        Returns true if the option is a Some value.
        """

    @abstractmethod
    def is_some_and(self, f: Callable[[T], bool]) -> bool:
        """
        Returns true if the option is a Some and the value inside of it matches a predicate.
        """

    @abstractmethod
    def is_null(self) -> TypeGuard[NullType]:
        """
        Returns true if the option is a Null value.
        """

    @abstractmethod
    def expect(self, msg: str) -> T:
        """
        Returns the contained Some value, consuming the self value.

        Panics if the value is a Null with a custom panic message provided by msg.
        """

    @abstractmethod
    def unwrap(self) -> T:
        """
        Returns the contained Some value, consuming the self value.

        Because this function may panic, its use is generally discouraged.
        Instead, prefer to use pattern matching and handle the Null case explicitly,
        or call unwrap_or, unwrap_or_else, or unwrap_or_default.

        Panics if the self value equals Null.
        """

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """
        Returns the contained Some value or a provided default.

        Arguments passed to unwrap_or are eagerly evaluated;
        if you are passing the result of a function call,
        it is recommended to use unwrap_or_else, which is lazily evaluated.
        """

    @abstractmethod
    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        """
        Returns the contained Some value or computes it from a closure.
        """

    @abstractmethod
    def map(self, f: Callable[[T], U]) -> Option[U]:
        """
        Maps an Option<T> to Option<U> by applying a function to a contained value.
        """

    @abstractmethod
    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        """
        Returns the provided default result (if Null),
        or applies a function to the contained value (if any).

        Arguments passed to map_or are eagerly evaluated;
        if you are passing the result of a function call,
        it is recommended to use map_or_else, which is lazily evaluated.
        """

    @abstractmethod
    def map_or_else(self, default: Callable[[], U], f: Callable[[T], U]) -> U:
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
    def and_then(self, f: Callable[[T], Option[U]]) -> Option[U]:
        """
        Returns Null if the option is Null,
        otherwise calls f with the wrapped value and returns the result.

        Some languages call this operation flatmap.

        Often used to chain fallible operations that may return Null.
        """

    @abstractmethod
    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
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
    def or_(self, optb: Option[T]) -> Option[T]:
        """
        Returns the option if it contains a value, otherwise returns optb.

        Arguments passed to or are eagerly evaluated;
        if you are passing the result of a function call,
        it is recommended to use or_else, which is lazily evaluated.
        """

    @abstractmethod
    def or_else(self, f: Callable[[], Option[T]]) -> Option[T]:
        """
        Returns the option if it contains a value,
        otherwise calls f and returns the result.
        """

    @abstractmethod
    def xor(self, optb: Option[T]) -> Option[T]:
        """
        Returns Some if exactly one of self, optb is Some, otherwise returns Null.
        """

    @abstractmethod
    def zip(self, other: Option[U]) -> Option[tuple[T, U]]:
        """
        Zips self with another Option.

        If self is Some(s) and other is Some(o),
        this method returns Some((s, o)).
        Otherwise, Null is returned.
        """

    @abstractmethod
    def zip_with(self, other: Option[U], f: Callable[[T, U], R]) -> Option[R]:
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


@dataclass
class Some(_BaseOption[T]):
    value: T

    def is_some(self) -> TypeGuard[Some[T]]:
        return True

    def is_some_and(self, f: Callable[[T], bool]) -> bool:
        return f(self.value)

    def is_null(self) -> TypeGuard[NullType]:
        return False

    def expect(self, msg: str) -> T:
        return self.value

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        return self.value

    def map(self, f: Callable[[T], U]) -> Option[U]:
        return Some(f(self.value))

    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        return f(self.value)

    def map_or_else(self, default: Callable[[], U], f: Callable[[T], U]) -> U:
        return f(self.value)

    def and_(self, optb: Option[U]) -> Option[U]:
        return optb

    def and_then(self, f: Callable[[T], Option[U]]) -> Option[U]:
        return f(self.value)

    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        return Some(self.value) if predicate(self.value) else Null

    def or_(self, optb: Option[T]) -> Option[T]:
        return self

    def or_else(self, f: Callable[[], Option[T]]) -> Option[T]:
        return self

    def xor(self, optb: Option[T]) -> Option[T]:
        return self if optb.is_null() else Null

    def zip(self, other: Option[U]) -> Option[tuple[T, U]]:
        match other:
            case Some(value):
                return Some((self.value, value))
            case _:
                return Null

    def zip_with(self, other: Option[U], f: Callable[[T, U], R]) -> Option[R]:
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
        ...

    @overload
    def flatten(self: Some[Some[U]]) -> Some[U]:
        ...

    @overload
    def flatten(self: Some[Option[U]]) -> Option[U]:
        ...

    def flatten(self: Some[Any]) -> Any:
        match self:
            case Some(NullType()):
                return Null
            case Some(Some(val)):
                return Some(val)
            case _:
                # it will never happen
                raise


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

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        return f()

    def map(self, f: Callable[[Any], U]) -> Option[U]:
        return self

    def map_or(self, default: U, f: Callable[[Any], U]) -> U:
        return default

    def map_or_else(self, default: Callable[[], U], f: Callable[[Any], U]) -> U:
        return default()

    def and_(self, optb: Option[U]) -> Option[U]:
        return self

    def and_then(self, f: Callable[[Any], Option[U]]) -> Option[U]:
        return self

    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        return self

    def or_(self, optb: Option[T]) -> Option[T]:
        return optb

    def or_else(self, f: Callable[[], Option[T]]) -> Option[T]:
        return f()

    def xor(self, optb: Option[T]) -> Option[T]:
        return self if optb.is_null() else optb

    def zip(self, other: Option[U]) -> Option[tuple[Any, U]]:
        return Null

    def zip_with(self, other: Option[U], f: Callable[[Any, U], R]) -> Option[R]:
        return Null

    def unzip(self) -> tuple[NullType, NullType]:
        return (Null, Null)

    def flatten(self: _BaseOption[_BaseOption[Any]]) -> NullType:
        return Null


Option = Some[T] | NullType

Null = NullType()

P = ParamSpec("P")


def to_option(f: Callable[P, T]) -> Callable[P, Option[T]]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return Some(f(*args, **kwargs))
        except:
            return Null

    return wrapper
