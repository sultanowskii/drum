from argparse import ArgumentParser

from drum.machine.io import OutputFormat
from drum.machine.run import run
from drum.util.io import eprint
from drum.util.log import setup_logger


def get_parser() -> ArgumentParser:
    parser = ArgumentParser()

    parser.add_argument(
        'compiled_file',
        type=str,
        help='Compiled (.drc) file',
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Input data file',
    )
    parser.add_argument(
        '-O',
        '--output-format',
        type=str,
        choices=[of.value.alias for of in OutputFormat],
        default=OutputFormat.STR.value.alias,
        help='Output data format',
    )
    parser.add_argument(
        '-L',
        '--logfile',
        type=str,
        default=None,
        help='Output data format',
    )

    return parser


def cli() -> None:
    parser = get_parser()

    args = parser.parse_args()

    compiled_file = args.compiled_file
    input_file = args.input_file

    output_format_raw = args.output_format
    output_format, err = OutputFormat.get_by_alias(output_format_raw)
    if err is not None:
        eprint('invalid output format')
        return

    logfile = args.logfile

    setup_logger('machine', logfile=logfile)

    error = run(compiled_file, input_file, output_format)

    if error is not None:
        eprint(error)


if __name__ == '__main__':
    cli()
