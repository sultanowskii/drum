

from json import dumps, loads

from drum.common.arch import Executable
from drum.common.fmt import fmt_const, fmt_instruction
from drum.util.io import read_from_file, write_to_file


def read_src(file: str) -> str:
    """Reads source (.dr) file."""
    return read_from_file(file)


def write_compiled(file: str, exe: Executable) -> None:
    """Writes compiled (.drc) file."""
    start = exe.start
    program = exe.program

    formatted_program = []
    for word in program:
        formatted_word, _ = fmt_const(word) if len(word) == 1 else fmt_instruction(word)
        f = dict(
            raw=word,
            formatted=formatted_word,
        )
        formatted_program.append(f)

    result = dict(
        start=start,
        program=formatted_program,
    )

    write_to_file(file, dumps(result, indent=2))


def read_compiled(file: str) -> Executable:
    """Reads compiled (.drc) file."""
    raw_data = read_from_file(file)
    data = loads(raw_data)

    start = data['start']
    program = data['program']

    simplified_program = []
    for word in program:
        simplified_program.append(word['raw'])

    return Executable(
        start,
        simplified_program,
    )
