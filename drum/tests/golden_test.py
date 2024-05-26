from contextlib import redirect_stdout
from io import StringIO
import os
import tempfile

import pytest

from drum.compiler import compile
from drum.machine import run as machine
from drum.machine.io import OutputFormat
from drum.util.io import read_from_file, write_to_file

SOURCE = 'code.dr'
COMPILED = 'code.drc'
LOGFILE = 'log.log'
INPUT = 'input.txt'
OUTPUT = 'output.txt'


@pytest.mark.golden_test('golden/*.yaml')
def test_compiler_and_machine(golden) -> None:
    """
    Golden tests that cover translator and machine.

    Input:
    - `in_source_code`: source code to compile and execute (`.dr`)
    - `in_input_data`: data directed to stdin

    Expected output:
    - `out_compiled`: compiled code (`.drc`)
    - `out_log`: execution log
    - `out_output`: translation&execution ouput
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        source_code = os.path.join(tmpdir, SOURCE)
        input_data = os.path.join(tmpdir, INPUT)
        target = os.path.join(tmpdir, COMPILED)
        logfile = os.path.join(tmpdir, LOGFILE)

        write_to_file(source_code, golden['in_source_code'])
        write_to_file(input_data, golden['in_input_data'])

        with redirect_stdout(StringIO()) as stdout:
            error = compile.run(
                source_code,
                target,
            )
            assert error is None

            print('============')

            error = machine.run(
                target,
                input_data,
                output_format=OutputFormat.get_by_alias(golden['in_output_format'])[0],
                logfile=logfile,
                log_level=golden['in_log_level'],
            )
            assert error is None

        assert read_from_file(target) == golden['out_compiled']
        assert read_from_file(logfile) == golden['out_log']
        assert stdout.getvalue() == golden['out_output']
