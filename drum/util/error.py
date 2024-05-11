from typing import TypeVar

T = TypeVar('T')

# Error type. None represents that error doesn't exist.
Error = str | None

# Type wrapper.
# Useful for functions that could potentially return an error.
Result = tuple[T, Error]
