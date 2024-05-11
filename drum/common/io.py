

from json import dumps, loads
from typing import Any

from drum.util.io import read_from_file, write_to_file


def read_src(file: str) -> str:
    """Reads source (.dr) file."""
    return read_from_file(file)


def write_compiled(file: str, compiled: dict[Any, Any]) -> None:
    """Writes compiled (.drc) file."""
    write_to_file(file, dumps(compiled, indent=2))


def read_compiled(file: str) -> dict[Any, Any]:
    """Reads compiled (.drc) file."""
    raw_data = read_from_file(file)
    return loads(raw_data)
