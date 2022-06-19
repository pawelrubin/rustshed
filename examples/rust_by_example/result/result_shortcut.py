from enum import Enum, auto
import math

from rustshed import Result, Err, Ok, result_shortcut, Panic


class MathError(Enum):
    DivisionByZero = auto()
    NonPositiveLogarithm = auto()
    NegativeSquareRoot = auto()


MathResult = Result[float, MathError]


def div(x: float, y: float) -> MathResult:
    if y == 0.0:
        return Err(MathError.DivisionByZero)
    return Ok(x / y)


def sqrt(x: float) -> MathResult:
    if x < 0.0:
        return Err(MathError.NegativeSquareRoot)
    return Ok(math.sqrt(x))


def ln(x: float) -> MathResult:
    if x <= 0.0:
        return Err(MathError.NonPositiveLogarithm)
    return Ok(math.log(x))


@result_shortcut
def op_(x: float, y: float) -> MathResult:
    # if `div` "fails", then `DivisionByZero` will be `return`ed
    ratio = div(x, y).Q

    # if `ln` "fails", then `NonPositiveLogarithm` will be `return`ed
    ln_value = ln(ratio).Q

    return sqrt(ln_value)


def op(x: float, y: float) -> None:
    """`op(x, y)` === `sqrt(ln(x / y))`"""
    match op_(x, y):
        case Err(why):
            match why:
                case MathError.DivisionByZero:
                    raise Panic("division by zero")
                case MathError.NonPositiveLogarithm:
                    raise Panic("logarithm of non-positive number")
                case MathError.NegativeSquareRoot:
                    raise Panic("square root of negative number")
        case Ok(value):
            print(value)


if __name__ == "__main__":
    op(10.0, 1.0)
