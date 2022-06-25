# rustshed

[![Python 3.10](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![codecov](https://codecov.io/gh/pawelrubin/rustshed/branch/main/graph/badge.svg?token=LV5XXHDSF5)](https://codecov.io/gh/pawelrubin/rustshed)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/pawelrubin/rustshed/blob/main/LICENSE)

A collection of Rust types in Python with complete type annotations.

### Supported Types

- Option
- Result

## Install

```shell
pip install rustshed
```


## Examples

### Option

The `Option` type represents an optional value: every `Option[T]` is either `Some[T]` and contains a value of type `T`, or `Null` (`None` in Rust), and does not.

```Python
from typing import SupportsIndex, TypeVar

from rustshed import Null, Option, Some

T = TypeVar("T")


class SafeList(list[T]):
    def get(self, index: SupportsIndex) -> Option[T]:
        try:
            return Some(self[index])
        except IndexError:
            return Null

a_list = SafeList([2, 1, 3, 7])
print(a_list.get(1))  # Some(value=1)
print(a_list.get(420))  # Null
```

### Result

The `Result` is the type used for returning and propagating errors: every `Result[T, E]` is either `Ok[T]`, representing success and containing a value of type `T`, or `Err[E]`, representing failure and containing an error of type `E`.

```python
from rustshed import to_result, Result


@to_result[ValueError]
def parse(x: str) -> int:
    return int(x)


def multiply(a: str, b: str) -> Result[int, str]:
    # try to parse two strings and multiply them
    # map a possible error to str
    return parse(a).and_then(lambda n: parse(b).map(lambda m: n * m)).map_err(str)


print(multiply("21", "2"))  # Ok(value=42)
print(multiply("2!", "2"))  # Err(error="invalid literal for int() with base 10: '2!'")
```

### Rust's question mark (?) operator

The question mark (`?`) operator in Rust hides some of the boilerplate of propagating errors up the call stack. Implementing this operator in Python would require changes to the language grammar, hence in **rustshed** it had to be implemented differently.

### Q property

The question mark's functionality has been implemented via the `Q` property (for both `Option` and `Result` types) combined with the `rustshed.result_shortcut` or `rustshed.option_shortcut` decorator.


```python
from rustshed import Ok, Result, to_result, result_shortcut


@to_result[ValueError]
def parse(x: str) -> int:
    return int(x)


# explicit early error return with match statements
def try_to_parse_early_return(a: str, b: str) -> Result[int, ValueError]:
    match parse(a):
        case Ok(value):
            x = value
        case err:
            return err

    match parse(b):
        case Ok(value):
            y = value
        case err:
            return err

    return Ok(x + y)


# early error return using the Q property
@result_shortcut
def try_to_parse(a: str, b: str) -> Result[int, ValueError]:
    x = parse(a).Q
    y = parse(b).Q
    return Ok(x + y)

```
