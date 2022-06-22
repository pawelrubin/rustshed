from dataclasses import dataclass
from functools import partial
from math import sqrt
from typing import Callable, SupportsIndex, TypeVar

import pytest

from rustshed import Null, Option, Panic, Some, option_shortcut, to_option


def test_is_some() -> None:
    x: Option[int] = Some(2)
    assert x.is_some() is True

    x = Null
    assert x.is_some() is False


def test_is_some_and() -> None:
    greater_than_one: Callable[[int], bool] = lambda x: x > 1

    x: Option[int] = Some(2)
    assert x.is_some_and(greater_than_one) is True

    x = Some(0)
    assert x.is_some_and(greater_than_one) is False

    x = Null
    assert x.is_some_and(greater_than_one) is False


def test_is_null() -> None:
    x: Option[int] = Some(2)
    assert x.is_null() is False

    x = Null
    assert x.is_null() is True


def test_expect() -> None:
    x: Option[str] = Some("value")
    assert x.expect("fruits are healthy") == "value"

    x = Null
    with pytest.raises(Panic) as panic:
        x.expect("fruits are healthy")

    assert str(panic.value) == "fruits are healthy"


def test_unwrap() -> None:
    x: Option[str] = Some("air")
    assert x.unwrap() == "air"

    x = Null
    with pytest.raises(Panic):
        x.unwrap()


def test_unwrap_or() -> None:
    assert Some("car").unwrap_or("bike") == "car"
    assert Null.unwrap_or("bike") == "bike"


def test_unwrap_or_else() -> None:
    k = 10
    assert Some(4).unwrap_or_else(lambda: 2 * k) == 4
    assert Null.unwrap_or_else(lambda: 2 * k) == 20


def test_map() -> None:
    maybe_some_string = Some("Hello_ World!")
    maybe_some_len = maybe_some_string.map(len)
    assert maybe_some_len == Some(13)


def test_map_or() -> None:
    x: Option[str] = Some("foo")
    assert x.map_or(42, len) == 3

    x = Null
    assert x.map_or(42, len) == 42


def test_map_or_else() -> None:
    k = 21

    x: Option[str] = Some("foo")
    assert x.map_or_else(lambda: 2 * k, len) == 3

    x = Null
    assert x.map_or_else(lambda: 2 * k, len) == 42


def test_and() -> None:
    x: Option[int] = Some(2)
    y: Option[str] = Null
    assert x.and_(y) == Null

    x = Null
    y = Some("foo")
    assert x.and_(y) == Null

    x = Some(2)
    y = Some("foo")
    assert x.and_(y) == Some("foo")

    x = Null
    y = Null
    assert x.and_(y) == Null


def test_and_then() -> None:
    T = TypeVar("T")

    class SafeList(list[T]):
        def get(self, index: SupportsIndex) -> Option[T]:
            try:
                return Some(self[index])
            except IndexError:
                return Null

    def sqrt_then_to_string(x: float) -> Option[str]:
        return to_option(sqrt)(x).map(str)

    assert Some(16).and_then(sqrt_then_to_string) == Some("4.0")
    assert Some(-1).and_then(sqrt_then_to_string) == Null  # sqrt of -1!
    assert Null.and_then(sqrt_then_to_string) == Null

    arr_2d = SafeList([SafeList(["A0", "A1"]), SafeList(["B0", "B1"])])

    item_0_1 = arr_2d.get(0).and_then(partial(SafeList[str].get, index=1))
    assert item_0_1 == Some("A1")

    item_2_0 = arr_2d.get(2).and_then(partial(SafeList[str].get, index=0))
    assert item_2_0 == Null


def test_filter() -> None:
    def is_even(n: int) -> bool:
        return n % 2 == 0

    assert Null.filter(is_even) == Null
    assert Some(3).filter(is_even) == Null
    assert Some(4).filter(is_even) == Some(4)


def test_or() -> None:
    x: Option[int] = Some(2)
    y: Option[int] = Null
    assert x.or_(y) == Some(2)

    x = Null
    y = Some(100)
    assert x.or_(y) == Some(100)

    x = Some(2)
    y = Some(100)
    assert x.or_(y) == Some(2)

    x = Null
    y = Null
    assert x.or_(y) == Null


def test_or_else() -> None:
    def nobody() -> Option[str]:
        return Null

    def vikings() -> Option[str]:
        return Some("vikings")

    assert Some("barbarians").or_else(vikings) == Some("barbarians")
    assert Null.or_else(vikings) == Some("vikings")
    assert Null.or_else(nobody) == Null


def test_xor() -> None:
    x: Option[int] = Some(2)
    y: Option[int] = Null
    assert x.xor(y) == Some(2)

    x = Null
    y = Some(2)
    assert x.xor(y) == Some(2)

    x = Some(2)
    y = Some(2)
    assert x.xor(y) == Null

    x = Null
    y = Null
    assert x.xor(y) == Null


def test_zip() -> None:
    x = Some(1)
    y = Some("hi")
    z = Null

    assert x.zip(y) == Some((1, "hi"))
    assert x.zip(z) == Null
    assert z.zip(z) == Null


def test_zip_with() -> None:
    @dataclass
    class Point:
        x: float
        y: float

    x = Some(17.5)
    y = Some(42.5)

    assert x.zip_with(y, Point) == Some(Point(17.5, 42.5))
    assert x.zip_with(Null, Point) == Null
    assert Null.zip_with(x, Point) == Null
    assert Null.zip_with(Null, Point) == Null


def test_unzip() -> None:
    x = Some((1, "hi"))
    y = Null

    assert x.unzip() == (Some(1), Some("hi"))
    assert y.unzip() == (Null, Null)
    assert Some(1).unzip() == (Null, Null)  # type: ignore


def test_flatten() -> None:
    x: Option[Option[int]] = Some(Some(6))
    assert x.flatten() == Some(6)

    x = Some(Null)
    assert x.flatten() == Null

    x = Null
    assert x.flatten() == Null

    y = Some(Some(2))
    assert y.flatten() == Some(2)

    z: Option[Option[Option[int]]] = Some(Some(Some(6)))
    assert z.flatten() == Some(Some(6))
    assert z.flatten().flatten() == Some(6)


def test_option_shortcut() -> None:
    def sqrt_then_to_string(x: float) -> Option[str]:
        return to_option(sqrt)(x).map(str)

    @option_shortcut
    def operation(x: float) -> Option[str]:
        sq = sqrt_then_to_string(x).Q
        print(sq)
        return Some(sq)

    assert operation(16) == Some("4.0")
    assert operation(-2) == Null


def test_null_to_str() -> None:
    assert str(Null) == "Null"
