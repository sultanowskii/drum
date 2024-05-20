from drum.common.io import read_compiled
from drum.machine.machine import exec_program
from drum.util.error import Error


def run(compiled_file: str, input_file: str) -> Error:
    exe = read_compiled(compiled_file)

    program = exe['program']
    start = exe['start']

    # TODO: parse input_file and pass
    exec_program(program, start, [])

    return None
