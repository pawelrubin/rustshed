from rustshed import (
    Err,
    Null,
    NullType,
    Ok,
    Option,
    Result,
    Some,
    is_err,
    is_null,
    is_ok,
    is_some,
)


def test_is_some() -> None:
    x: Option[int] = Some(5)

    assert is_some(x) is True
    assert is_null(x) is False

    if is_some(x):
        # if the type is not narrowed down correctly
        # mypy would throw an error
        _y: Some[int] = x


def test_is_null() -> None:
    x: Option[int] = Null

    assert is_some(x) is False
    assert is_null(x) is True

    if is_null(x):
        # if the type is not narrowed down correctly
        # mypy would throw an error
        _z: NullType = x


def test_is_ok() -> None:
    x: Result[int, str] = Ok(5)

    assert is_ok(x) is True
    assert is_err(x) is False

    if is_ok(x):
        # if the type is not narrowed down correctly
        # mypy would throw an error
        _y: Ok[int] = x


def test_is_err() -> None:
    x: Result[int, str] = Err("foo")

    assert is_ok(x) is False
    assert is_err(x) is True

    if is_err(x):
        # if the type is not narrowed down correctly
        # mypy would throw an error
        _z: Err[str] = x
