from sys import argv

from drum.common.util.files import read_from_file, write_all_to_file
from drum.compiler.lexer import Lexer, lex_top


def cli() -> None:
    if len(argv) != 3:
        print(f'Usage: {argv[0]} input_file output_file')
        exit(1)

    input_file = argv[1]
    output_file = argv[2]

    text = read_from_file(input_file)

    lexer = Lexer(text, lex_top)
    tokens = lexer.lex()

    write_all_to_file(output_file, map(lambda t: str(t), tokens))


if __name__ == '__main__':
    cli()
