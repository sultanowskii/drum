import re
from string import ascii_letters, digits
from typing import Callable

from drum.compiler.tokens import Token, TokenType

# End of file
EOF = '\0'
# Lexer state function
StateFunction = Callable[['Lexer'], 'StateFunction'] | None

# Keyword start symbols
START_SYMBOLS = ascii_letters + '_'
# Keyword symbols
SYMBOLS = START_SYMBOLS + digits

# Number symbols
NUMBER_SYMBOLS = digits
SIGN_SYMBOLS = '+-'
NUMBER_SYMBOLS_EXTENDED = NUMBER_SYMBOLS + SIGN_SYMBOLS

# Whitespace symbols & newline
WHITESPACES = ' \t'
WHITESPACES_NEWLINES = WHITESPACES + '\n'

# Label token regex
LABEL_REGEX = re.compile(rf'^[{START_SYMBOLS}]{{1}}[{SYMBOLS}]+:')


class Lexer:
    """Lexing state class."""

    # Text to be lexed
    text: str
    # Token start position
    token_start: int
    # Text position
    position: int
    # List of parsed tokens
    tokens: list[Token]
    # Function that represents current state
    state: StateFunction

    def __init__(self, text: str, state: StateFunction) -> None:
        self.text = text
        self.token_start = 0
        self.position = 0
        self.state = state
        self.tokens = []

    def lex(self) -> list[Token]:
        """Lexes text."""
        while self.state is not None:
            self.state = self.state(self)
        return self.tokens

    def next(self) -> str:
        """Consumes symbol if possible."""
        if self.position >= len(self.text):
            self.position = len(self.text) + 1
            return EOF

        sym = self.text[self.position]
        self.position += 1
        return sym

    def go_back(self) -> None:
        """Goes back by one symbol."""
        self.position -= 1

    def omit(self) -> None:
        """Omits unprocessed symbols."""
        self.token_start = self.position

    def skip_if_valid(self, whitelist: str) -> bool:
        """Skips symbols while they are in the whitelist."""
        res = self.consume_if_valid(whitelist)
        self.omit()
        return res

    def skip_while_valid(self, whitelist: str) -> None:
        """Skips symbols while they are in the whitelist."""
        self.consume_while_valid(whitelist)
        self.omit()

    def skip_until(self, blacklist: str) -> None:
        """Skips symbols until they are not in the blacklist."""
        self.consume_until(blacklist)
        self.omit()

    def peek(self) -> str:
        """Returns the next symbol if possible without consumption."""
        sym = self.next()
        self.go_back()
        return sym

    def consume_if_valid(self, whitelist: str) -> bool:
        """Consumes symbol if it's in the whitelist."""
        sym = self.next()
        if sym in whitelist:
            return True

        self.go_back()
        return False

    def consume_while_valid(self, whitelist: str) -> None:
        """Consumes symbols while they are in the whitelist."""
        sym = self.next()
        while sym in whitelist:
            sym = self.next()

        self.go_back()

    def consume_until(self, blacklist: str) -> None:
        """Consumes symbols until they are not in the blacklist."""
        sym = self.next()
        while sym is not EOF and sym not in blacklist:
            sym = self.next()

        self.go_back()

    def save_token(self, token_type: TokenType) -> None:
        """Saves currently processed token and moves on."""
        self.tokens.append(Token(
            self.text[self.token_start:self.position],
            token_type,
        ))
        self.token_start = self.position

    def error(self, message: str) -> StateFunction:
        """Returns a StateFunction that'll terminate lexing and save an error as a token."""
        def f(lexer: Lexer) -> StateFunction:
            lexer.tokens.append(Token(
                f'{message}: {lexer.peek()} (position {lexer.position})',
                TokenType.ERROR,
            ))
            return None

        return f


def lex_comment(lexer: Lexer) -> StateFunction:
    """Lexes comment."""
    if lexer.next() != ';':
        return lexer.error('invalid start of comment (; expected)')

    lexer.skip_while_valid(WHITESPACES)
    lexer.skip_until('\n')

    return lex_top


def lex_label(lexer: Lexer) -> StateFunction:
    """Lexes label."""
    lexer.consume_while_valid(SYMBOLS)

    if lexer.next() == ':':
        lexer.save_token(TokenType.LABEL)
        return lex_top

    return lexer.error('invalid end of label (: expected)')


def lex_argument_comma(lexer: Lexer) -> StateFunction:
    """Lexes comma between instruction arguments."""
    lexer.skip_while_valid(WHITESPACES)
    lexer.skip_if_valid(',')
    lexer.skip_while_valid(WHITESPACES)

    return lex_argument


def lex_argument_number(lexer: Lexer) -> StateFunction:
    """Lexes number (as instruction argument)."""
    lexer.consume_if_valid(SIGN_SYMBOLS)
    lexer.consume_while_valid(NUMBER_SYMBOLS)
    lexer.save_token(TokenType.ARGUMENT_NUMBER)

    return lex_argument_comma


def lex_argument_label(lexer: Lexer) -> StateFunction:
    """Lexes label reference (as instruction argument)."""
    lexer.consume_while_valid(SYMBOLS)
    lexer.save_token(TokenType.ARGUMENT_LABEL)

    return lex_argument_comma


def lex_argument_string(lexer: Lexer) -> StateFunction:
    """Lexes string (as instruction argument)."""
    if lexer.next() != '"':
        return lexer.error('invalid start of string (" expected)')

    while True:
        symbol = lexer.next()
        if symbol == EOF:
            break
        if symbol == '"':
            lexer.save_token(TokenType.ARGUMENT_STRING)
            break

    return lex_argument_comma


def lex_argument_register(lexer: Lexer) -> StateFunction:
    """Lexes register (as instruction argument)."""
    if lexer.next() != '%':
        return lexer.error('invalid register prefix (%% expected)')

    if lexer.next() not in START_SYMBOLS:
        return lexer.error('invalid symbol while lexing register')

    lexer.consume_while_valid(SYMBOLS)

    lexer.save_token(TokenType.ARGUMENT_REGISTER)

    return lex_argument_comma


def lex_argument(lexer: Lexer) -> StateFunction:
    """Lexes instruction argument."""
    if lexer.peek() in NUMBER_SYMBOLS_EXTENDED:
        return lex_argument_number

    if lexer.peek() in START_SYMBOLS:
        return lex_argument_label

    if lexer.peek() == '%':
        return lex_argument_register

    if lexer.peek() == '"':
        return lex_argument_string

    lexer.skip_while_valid(WHITESPACES_NEWLINES)

    return lex_top


def lex_instruction(lexer: Lexer) -> StateFunction:
    """Lexes instruction."""
    lexer.consume_while_valid(SYMBOLS)

    lexer.save_token(TokenType.INSTRUCTION)

    lexer.skip_while_valid(WHITESPACES)

    if lexer.peek() == '\n':
        return lex_top

    if lexer.peek() == EOF:
        return None

    return lex_argument


def lex_top(lexer: Lexer) -> StateFunction:
    """Top-level lexer part."""
    lexer.skip_while_valid(WHITESPACES_NEWLINES)

    if lexer.peek() == ';':
        return lex_comment

    if lexer.peek() in START_SYMBOLS:
        if LABEL_REGEX.match(lexer.text[lexer.position:]):
            return lex_label
        return lex_instruction

    if lexer.peek() == EOF:
        return None

    return lexer.error('unexpected symbol while lexing top-level')
