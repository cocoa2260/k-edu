from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass
class Result(Generic[T]):
    data: T
    success: bool = True

text_result = Result[str]("완료")
list_result = Result[list[int]]([1, 2, 3])
print(text_result)
print(list_result)
