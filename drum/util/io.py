from sys import stderr
from typing import Any


def read_from_file(file: str) -> str:
    """Reads from given file."""
    with open(file, 'r') as f:
        return f.read().strip()


def write_to_file(file: str, text: str) -> None:
    """Reads from give file."""
    with open(file, 'w') as f:
        f.write(text)


def eprint(*args: Any, **kwargs: Any) -> None:  # noqa: ANN401
    """`print()` wrapper that writes to stderr instead."""
    print(*args, file=stderr, **kwargs)
