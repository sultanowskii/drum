from dataclasses import dataclass
from enum import Enum
from typing import Callable

from drum.util.error import Result


def _normalize_data_to_alignment(data: list[int], align: int) -> list[int]:
    tail_len = (align - (len(data) % align)) % align
    tail = [0] * tail_len
    return data + tail


@dataclass
class OFDef:
    alias: str
    print_output_data: Callable[[list[int]], None]


def _print_output_data_as_str(output_data: list[int]) -> None:
    print(''.join(chr(c) for c in output_data))


def _print_output_data_as_ints(output_data: list[int]) -> None:
    normalized_output_data = _normalize_data_to_alignment(output_data, 4)
    result = []

    for i in range(0, len(normalized_output_data), 4):
        n = 0
        for j in range(4):
            n += normalized_output_data[i + j] * (256 ** j)
        result.append(str(n))

    print(', '.join(n for n in result))


def _print_output_data_as_hex_ints(output_data: list[int]) -> None:
    normalized_output_data = _normalize_data_to_alignment(output_data, 4)
    result = []

    for i in range(0, len(normalized_output_data), 4):
        n = 0
        for j in range(4):
            n += normalized_output_data[i + j] * (256 ** j)
        result.append(hex(n))

    print(', '.join(n for n in result))


def _print_output_data_as_bytes(output_data: list[int]) -> None:
    print(', '.join(str(c) for c in output_data))


def _print_output_data_as_hex_bytes(output_data: list[int]) -> None:
    print(', '.join(hex(c) for c in output_data))


class OutputFormat(Enum):
    STR = OFDef('str', _print_output_data_as_str)
    INTS = OFDef('ints', _print_output_data_as_ints)
    HEX_INTS = OFDef('hex-ints', _print_output_data_as_hex_ints)
    BYTESS = OFDef('bytes', _print_output_data_as_bytes)
    HEX_BYTES = OFDef('hex-bytes', _print_output_data_as_hex_bytes)

    @staticmethod
    def get_by_alias(alias: str) -> Result['OutputFormat']:
        """Returns output format with provided alias. Error if it doesn't exist."""
        for of in OutputFormat:
            if of.value.alias == alias:
                return of, None

        return OutputFormat.STR, f"output format {alias} doesn\'t exist"
