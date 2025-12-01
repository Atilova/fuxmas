import re


_PASCAL_TO_SNAKE_CASE_PATTERN = re.compile(
   r'(?<=[a-z0-9])(?=[A-Z])'
)


def from_pascal_to_snake_case(value: str):
   return _PASCAL_TO_SNAKE_CASE_PATTERN.sub("_", value).lower()
