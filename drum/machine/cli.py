from sys import argv

from drum.machine.run import run
from drum.util.io import eprint


def cli() -> None:
    if len(argv) != 3:
        print(f'usage: {argv[0]} compiled_file[.drc] input_file')
        return

    compiled_file = argv[1].strip()
    input_file = argv[2].strip()

    error = run(compiled_file, input_file)

    if error is not None:
        eprint(error)


if __name__ == '__main__':
    cli()
