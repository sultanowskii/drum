from sys import argv

from drum.compiler.compile import run
from drum.util.io import eprint


def cli() -> None:
    if len(argv) != 3:
        print(f'usage: {argv[0]} src_file[.dr] output_file[.drc]')
        return

    src_file = argv[1].strip()
    output_file = argv[2].strip()

    if src_file == output_file:
        eprint("src file and output file shouldn't be equal")
        return

    error = run(src_file, output_file)

    if error is not None:
        eprint(error)


if __name__ == '__main__':
    cli()
