import os
import sys
from dataclasses import dataclass
from enum import Enum, auto
from math import sqrt
from pathlib import Path
from typing import Callable

import pytest

from rustshed import (
    Err,
    Null,
    Ok,
    Option,
    Panic,
    Result,
    Some,
    result_shortcut,
    to_io_result,
    to_result,
)


def test_is_ok() -> None:
    x: Result[int, str] = Ok(-3)
    assert x.is_ok() is True

    x = Err("Some error message")
    assert x.is_ok() is False


def test_is_ok_and() -> None:
    greater_than_one: Callable[[int], bool] = lambda x: x > 1

    x: Result[int, str] = Ok(2)
    assert x.is_ok_and(greater_than_one) is True

    x = Ok(0)
    assert x.is_ok_and(greater_than_one) is False

    x = Err("hey")
    assert x.is_ok_and(greater_than_one) is False


def test_is_err() -> None:
    x: Result[int, str] = Ok(-3)
    assert x.is_err() is False

    x = Err("Some error message")
    assert x.is_err() is True


def test_is_err_and() -> None:
    class ErrorKind(Enum):
        NotFound = auto()
        PermissionDenied = auto()

    @dataclass
    class Error:
        kind: ErrorKind

    is_not_found_error: Callable[[Error], bool] = lambda x: x.kind == ErrorKind.NotFound

    x: Result[int, Error] = Err(Error(ErrorKind.NotFound))
    assert x.is_err_and(is_not_found_error) is True

    x = Err(Error(ErrorKind.PermissionDenied))
    assert x.is_err_and(is_not_found_error) is False

    x = Ok(123)
    assert x.is_err_and(is_not_found_error) is False


def test_ok() -> None:
    x: Result[int, str] = Ok(2)
    assert x.ok() == Some(2)

    x = Err("Nothing here")
    assert x.ok() == Null


def test_err() -> None:
    x: Result[int, str] = Ok(2)
    assert x.err() == Null

    x = Err("Nothing here")
    assert x.err() == Some("Nothing here")


def test_map() -> None:
    numbers_as_strs = ["1", "2", "E", "A", "5"]

    parse = to_result(int)

    numbers: list[int] = []
    for number_as_str in numbers_as_strs:
        match parse(number_as_str).map(lambda x: x**2):
            case Ok(value):
                numbers.append(value)
            case Err(_):
                continue

    assert numbers == [1, 4, 25]


def test_map_or() -> None:
    x: Result[str, str] = Ok("foo")
    assert x.map_or(42, len) == 3

    x = Err("bar")
    assert x.map_or(42, len) == 42


def test_map_or_else() -> None:
    k = 21

    x: Result[str, str] = Ok("foo")
    assert x.map_or_else(lambda _: k * 2, len) == 3

    x = Err("bar")
    assert x.map_or_else(lambda _: k * 2, len) == 42


def test_map_err() -> None:
    def stringify(x: int) -> str:
        return f"error code: {x}"

    x: Result[int, int] = Ok(2)
    assert x.map_err(stringify) == Ok(2)

    x = Err(13)
    assert x.map_err(stringify) == Err("error code: 13")


def test_inspect(capsys: pytest.CaptureFixture[str]) -> None:
    @to_result[ValueError]
    def parse(x: str) -> int:
        return int(x)

    _x: int = (
        parse("4")
        .inspect(lambda x: print(f"original: {x}"))
        .map(lambda x: pow(x, 3))
        .expect("failed to parse number")
    )
    assert capsys.readouterr().out == "original: 4\n"

    assert Err("foo").inspect(print) == Err("foo")


def test_inspect_err(capsys: pytest.CaptureFixture[str]) -> None:
    @to_io_result
    def read_to_str(path: str | Path) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read()

    read_to_str("address.txt").inspect_err(
        lambda e: print(f"failed to read file: {e}", file=sys.stderr)
    )
    assert (
        capsys.readouterr().err
        == "failed to read file: [Errno 2] No such file or directory: 'address.txt'\n"
    )
    assert Ok(5).inspect_err(print) == Ok(5)


def test_expect() -> None:
    x: Result[int, str] = Err("emergency failure")
    with pytest.raises(Panic) as panic:
        x.expect("Testing expect")

    assert str(panic.value) == "Testing expect"

    x = Ok(42)
    assert x.expect("Should succeed") == 42


def test_unwrap() -> None:
    x: Result[int, str] = Ok(2)
    assert x.unwrap() == 2

    x = Err("emergency failure")
    with pytest.raises(Panic) as panic:
        assert x.unwrap()

    assert str(panic.value) == "emergency failure"


def test_expect_err() -> None:
    x: Result[int, str] = Ok(10)

    with pytest.raises(Panic) as panic:
        assert x.expect_err("Testing expect_err")

    assert str(panic.value) == "Testing expect_err: 10"

    x = Err("error message")
    assert x.expect_err("should fail") == "error message"


def test_unwrap_err() -> None:
    x: Result[int, str] = Ok(2)

    with pytest.raises(Panic) as panic:
        assert x.unwrap_err()

    assert str(panic.value) == "2"

    x = Err("error message")
    assert x.unwrap_err() == "error message"


def test_and_() -> None:
    x: Result[int, str] = Ok(2)
    y: Result[str, str] = Err("late error")

    assert x.and_(y) == Err("late error")

    x = Err("early error")
    y = Ok("foo")
    assert x.and_(y) == Err("early error")

    x = Err("not a 2")
    y = Err("late error")
    assert x.and_(y) == Err("not a 2")

    x = Ok(2)
    y = Ok("different result type")
    assert x.and_(y) == Ok("different result type")


def test_and_then() -> None:
    def sqrt_then_to_string(x: float) -> Result[str, str]:
        return to_result[ValueError](sqrt)(x).map(str).map_err(str)

    assert Ok(16).and_then(sqrt_then_to_string) == Ok("4.0")
    assert Ok(-1).and_then(sqrt_then_to_string) == Err("math domain error")
    assert Err("not a number").and_then(sqrt_then_to_string) == Err("not a number")

    def path_stat(
        path: str | bytes | Path,
    ) -> Result[os.stat_result, FileNotFoundError]:
        return to_result[FileNotFoundError](os.stat)(path)

    root_modified_time: Result[float, FileNotFoundError] = path_stat("/").and_then(
        lambda stat: Ok(stat.st_mtime)
    )
    assert root_modified_time.is_ok()

    should_fail: Result[float, FileNotFoundError] = path_stat("/bad/path").and_then(
        lambda stat: Ok(stat.st_mtime)
    )
    assert should_fail.is_err()


def test_or() -> None:
    x: Result[int, str] = Ok(2)
    y: Result[int, str] = Err("late error")
    assert x.or_(y) == Ok(2)

    x = Err("Early error")
    y = Ok(2)
    assert x.or_(y) == Ok(2)

    x = Err("not a 2")
    y = Err("late error")
    assert x.or_(y) == Err("late error")

    x = Ok(2)
    y = Ok(100)
    assert x.or_(y) == Ok(2)


def test_or_else() -> None:
    def sq(x: int) -> Result[int, int]:
        return Ok(x * x)

    def err(x: int) -> Result[int, int]:
        return Err(x)

    assert Ok(2).or_else(sq).or_else(sq) == Ok(2)
    assert Ok(2).or_else(err).or_else(sq) == Ok(2)
    assert Err(3).or_else(sq).or_else(err) == Ok(9)
    assert Err(3).or_else(err).or_else(err) == Err(3)


def test_unwrap_or() -> None:
    default = 2
    x: Result[int, str] = Ok(9)
    assert x.unwrap_or(default) == 9

    x = Err("error")
    assert x.unwrap_or(default) == default


def test_unwrap_or_else() -> None:
    assert Ok(2).unwrap_or_else(len) == 2
    assert Err("foo").unwrap_or_else(len) == 3


def test_contains() -> None:
    x: Result[int, str] = Ok(2)
    assert x.contains(2) is True

    x = Ok(3)
    assert x.contains(2) is False

    x = Err("some error message")
    assert x.contains(2) is False


def test_contains_err() -> None:
    x: Result[int, str] = Ok(2)
    assert x.contains_err("Some error message") is False

    x = Err("Some error message")
    assert x.contains_err("Some error message") is True

    x = Err("Some other error message")
    assert x.contains_err("Some error message") is False


def test_transpose() -> None:
    x: Result[Option[int], str] = Ok(Some(5))
    y: Option[Result[int, str]] = Some(Ok(5))
    assert x.transpose() == y

    x = Ok(Null)
    assert x.transpose() == Null

    x = Err("foo")
    assert x.transpose() == Some(x)


def test_result_shortcut() -> None:
    def sqrt_then_to_string(x: float) -> Result[str, str]:
        return to_result[ValueError](sqrt)(x).map(str).map_err(str)

    @result_shortcut
    def operation(x: float) -> Result[str, str]:
        sq = sqrt_then_to_string(x).Q
        print(sq)
        return Ok(sq)

    assert operation(16) == Ok("4.0")
    assert operation(-2) == Err("math domain error")
