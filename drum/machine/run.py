from drum.common.io import read_compiled
from drum.machine.io import OutputFormat
from drum.machine.machine import exec_program
from drum.util.error import Error
from drum.util.io import read_from_file


def str_to_input_data(s: str) -> list[int]:
    """Transforms string to input data."""
    return [ord(c) for c in s] + [0]


def run(compiled_file: str, input_file: str, output_format: OutputFormat) -> Error:
    exe = read_compiled(compiled_file)
    input_data = str_to_input_data(read_from_file(input_file))

    program = exe['program']
    start = exe['start']

    output_data = exec_program(program, start, input_data)

    print('Output:')
    output_format.value.print_output_data(output_data)

    return None
