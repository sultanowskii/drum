from json import dumps
from sys import argv

from drum.common.util.io import eprint, read_from_file, write_to_file
from drum.compiler.lexer import Lexer, lex_top
from drum.compiler.tokens import TokenType
from drum.compiler.translator import Translator


def cli() -> None:
    if len(argv) != 3:
        print(f'usage: {argv[0]} input_file[.dr] output_file[.drc]')
        return

    input_file = argv[1].strip()
    output_file = argv[2].strip()

    if input_file == output_file:
        eprint("input file and output file shouldn't be equal")
        return

    text = read_from_file(input_file)

    lexer = Lexer(text, lex_top)
    tokens = lexer.lex()

    for token in tokens:
        if token.type == TokenType.ERROR:
            eprint(f'lexer error: {token.value}')
            return

    translator = Translator(tokens)
    exe, error = translator.translate()

    if error is not None:
        eprint(error)
        return

    write_to_file(
        output_file,
        dumps(
            dict(
                start=exe.start,
                program=exe.program,
            ),
            indent=2,
        ),
    )


if __name__ == '__main__':
    cli()
