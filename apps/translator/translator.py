from sys import argv

from apps.common.files import read_from_file, write_all_to_file
from apps.translator.lexer import Lexer, lex_top


def main() -> None:
    if len(argv) != 3:
        print('Usage: translator.py input_file output_file')
        exit(1)

    input_file = argv[1]
    output_file = argv[2]

    text = read_from_file(input_file)

    lexer = Lexer(text, lex_top)
    tokens = lexer.lex()

    write_all_to_file(output_file, map(lambda t: str(t), tokens))


if __name__ == '__main__':
    main()
