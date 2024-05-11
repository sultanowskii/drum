from drum.common.io import read_src, write_compiled
from drum.compiler.lexer import Lexer, lex_top
from drum.compiler.tokens import TokenType
from drum.compiler.translator import Translator
from drum.util.error import Error


def compile(input_file: str, output_file: str) -> Error:
    """
    Compiles code from `input_file` and writes the result ot `output_file`.

    If error is encountered, prints it and returns immediately.
    """
    text = read_src(input_file)

    lexer = Lexer(text, lex_top)
    tokens = lexer.lex()

    for token in tokens:
        if token.type == TokenType.ERROR:
            return f'lexer error: {token.value}'

    translator = Translator(tokens)
    exe, error = translator.translate()

    if error is not None:
        return f'translator error: {error}'

    write_compiled(
        output_file,
        dict(
            start=exe.start,
            program=exe.program,
        ),
    )

    return None
