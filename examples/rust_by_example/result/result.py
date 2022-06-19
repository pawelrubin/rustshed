from enum import Enum, auto
import math

from rustshed import Result, Err, Ok, Panic


class MathError(Enum):
    """Mathematical "errors" we want to catch"""

    DivisionByZero = auto()
    NonPositiveLogarithm = auto()
    NegativeSquareRoot = auto()


MathResult = Result[float, MathError]


def div(x: float, y: float) -> MathResult:
    if y == 0.0:
        # This operation would `fail`, instead let's return the reason of
        # the failure wrapped in `Err`
        return Err(MathError.DivisionByZero)

    # This operation is valid, return the result wrapped in `Ok`
    return Ok(x / y)


def sqrt(x: float) -> MathResult:
    if x < 0.0:
        return Err(MathError.NegativeSquareRoot)
    return Ok(math.sqrt(x))


def ln(x: float) -> MathResult:
    if x <= 0.0:
        return Err(MathError.NonPositiveLogarithm)
    return Ok(math.log(x))


def op(x: float, y: float) -> float:
    match div(x, y):
        case Err(why):
            raise Panic(why)
        case Ok(value):
            ratio = value

    match ln(ratio):
        case Err(why):
            raise Panic(why)
        case Ok(value):
            ln_value = value

    match sqrt(ln_value):
        case Err(why):
            raise Panic(why)
        case Ok(value):
            result = value

    return result


if __name__ == "__main__":
    # Will this fail?
    print(op(1.0, 10.0))
