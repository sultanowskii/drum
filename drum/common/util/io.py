from sys import stderr
from typing import Any, Iterable


def read_from_file(input_file: str) -> str:
    """Reads from give file."""
    with open(input_file, 'r') as f:
        return f.read().strip()


def write_to_file(output_file: str, text: str) -> None:
    """Reads from give file."""
    with open(output_file, 'w') as f:
        f.write(text)


def write_all_to_file(output_file: str, objects: Iterable[Any]) -> None:
    """Reads from give file."""
    with open(output_file, 'w') as f:
        for obj in objects:
            f.write(f'{obj}\n')


def eprint(*args, **kwargs) -> None:  # noqa: ANN002,ANN003
    """`print()` wrapper that writes to stderr instead."""
    print(*args, file=stderr, **kwargs)
