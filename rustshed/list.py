from typing import SupportsIndex, TypeVar

from rustshed.option_result import Null, Option, Some

T = TypeVar("T")


class SafeList(list[T]):
    def get(self, index: SupportsIndex) -> Option[T]:
        try:
            return Some(self[index])
        except IndexError:
            return Null
