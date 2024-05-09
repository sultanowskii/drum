from json import dumps
from sys import argv

from drum.common.util.files import read_from_file, write_to_file
from drum.compiler.lexer import Lexer, lex_top
from drum.compiler.translator import Translator


def cli() -> None:
    if len(argv) != 3:
        print(f'Usage: {argv[0]} input_file output_file')
        exit(1)

    input_file = argv[1]
    output_file = argv[2]

    text = read_from_file(input_file)

    lexer = Lexer(text, lex_top)
    tokens = lexer.lex()

    for token in tokens:
        print(token)

    translator = Translator(tokens)
    program, start = translator.translate()

    write_to_file(
        output_file,
        dumps(
            dict(
                start=start,
                program=program,
            ),
            indent=2,
        ),
    )


if __name__ == '__main__':
    cli()
