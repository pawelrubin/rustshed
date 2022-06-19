from rustshed import to_result


class ParseIntError(ValueError):
    ...


@to_result[ParseIntError]
def parse(s: str) -> int:
    try:
        return int(s)
    except ValueError as err:
        raise ParseIntError(str(err)) from None
