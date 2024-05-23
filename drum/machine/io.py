from dataclasses import dataclass
from enum import Enum
from typing import Callable

from drum.util.error import Result


def _normalize_data_to_alignment(data: list[int], align: int) -> list[int]:
    """Adds 0s to the end so that its length is divisible by align."""
    tail_len = (align - (len(data) % align)) % align
    tail = [0] * tail_len
    return data + tail


@dataclass
class OFDef:
    """Output format defenition."""
    alias: str
    fmt_output_data: Callable[[list[int]], str]


def _fmt_output_data_as_str(output_data: list[int]) -> str:
    """Formats output data as string (ASCII)."""
    return ''.join(chr(c) for c in output_data)


def _fmt_output_data_as_ints(output_data: list[int]) -> str:
    """Formats output data as ints (4-byte numbers)."""
    normalized_output_data = _normalize_data_to_alignment(output_data, 4)
    result = []

    for i in range(0, len(normalized_output_data), 4):
        n = 0
        for j in range(4):
            n += normalized_output_data[i + j] * (256 ** j)
        result.append(str(n))

    return ', '.join(n for n in result)


def _fmt_output_data_as_hex_ints(output_data: list[int]) -> str:
    """Formats output data as ints (4-byte numbers) in hex."""
    normalized_output_data = _normalize_data_to_alignment(output_data, 4)
    result = []

    for i in range(0, len(normalized_output_data), 4):
        n = 0
        for j in range(4):
            n += normalized_output_data[i + j] * (256 ** j)
        result.append(hex(n))

    return ', '.join(n for n in result)


def _fmt_output_data_as_bytes(output_data: list[int]) -> str:
    """Formats output data as bytes (1-byte numbers)."""
    return ', '.join(str(c) for c in output_data)


def _fmt_output_data_as_hex_bytes(output_data: list[int]) -> str:
    """Formats output data as bytes (1-byte numbers) in hex."""
    return ', '.join(hex(c) for c in output_data)


class OutputFormat(Enum):
    """Machine output format."""
    STR = OFDef('str', _fmt_output_data_as_str)
    INTS = OFDef('ints', _fmt_output_data_as_ints)
    HEX_INTS = OFDef('hex-ints', _fmt_output_data_as_hex_ints)
    BYTESS = OFDef('bytes', _fmt_output_data_as_bytes)
    HEX_BYTES = OFDef('hex-bytes', _fmt_output_data_as_hex_bytes)

    @staticmethod
    def get_by_alias(alias: str) -> Result['OutputFormat']:
        """Returns output format with provided alias. Error if it doesn't exist."""
        for of in OutputFormat:
            if of.value.alias == alias:
                return of, None

        return OutputFormat.STR, f"output format {alias} doesn\'t exist"
