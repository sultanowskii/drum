from sys import argv

from drum.machine.io import OutputFormat
from drum.machine.run import run
from drum.util.io import eprint


def cli() -> None:
    if len(argv) < 3:
        print(f'usage: {argv[0]} compiled_file[.drc] input_file [output_format]')
        return

    compiled_file = argv[1].strip()
    input_file = argv[2].strip()

    output_format = OutputFormat.STR

    if len(argv) >= 4:
        output_format_alias = argv[3].strip()

        output_format, err = OutputFormat.get_by_alias(output_format_alias)
        if err is not None:
            print(err)
            print(
                'valid values for output_format:',
                ' | '.join((of.value.alias for of in OutputFormat)),
            )
            return

    error = run(compiled_file, input_file, output_format)

    if error is not None:
        eprint(error)


if __name__ == '__main__':
    cli()
