from typing import Callable

from drum.common.arch import ArgsType, Op
from drum.compiler.tokens import Token, TokenType

Command = list[int]
RawCommand = list[int | str]
Program = list[Command | int]
RawProgram = list[RawCommand | int]
END = None

START_LABEL = '_start'


def resolve_labels_in_command(raw_command: RawCommand, labels: dict[str, int]) -> Command:
    """Returns command with resolved label references."""
    command = []

    for line in raw_command:
        if isinstance(line, int):
            command.append(line)
            continue

        if line not in labels.keys():
            print(f'undefined label: {line}')

        command.append(labels[line])

    return command


def resolve_labels_in_program(raw: RawProgram, labels: dict[str, int]) -> Program:
    """Resolves all label references in raw program - and returns the resulting one."""
    program: Program = []

    for line in raw:
        if isinstance(line, list):
            command = resolve_labels_in_command(line, labels)
            program.append(command)
        else:
            program.append(line)

    return program


class Translator:
    """Token to code translator."""

    pos: int
    tokens: list[Token]

    def __init__(self, token_list: list[Token]) -> None:
        self.tokens = token_list
        self.pos = 0

    def next(self) -> Token:
        """Goes to the next token if possible."""
        value = self.tokens[self.pos]
        self.pos += 1
        return value

    def go_back(self) -> None:
        """Goes back by one token."""
        self.pos -= 1

    def peek(self) -> Token:
        """Returns the next symbol if possible without consumption."""
        value = self.next()
        self.go_back()
        return value

    def translate_register_argument(self) -> int | str:
        """Translates register argument."""
        register = self.next().value
        return int(register[1])

    def translate_immediate_argument(self) -> int | str:
        """Translates immediate argument."""
        token = self.next()
        try:
            return int(token.value)
        except ValueError:
            # label, probably.
            return token.value

    def get_args_type_translator_list(self, args_type: ArgsType) -> list[Callable[[], int | str]]:
        """Returns proper list of translators for specific command args type."""
        return {
            ArgsType.ZERO: [],
            ArgsType.RRR: [
                self.translate_register_argument,
                self.translate_register_argument,
                self.translate_register_argument,
            ],
            ArgsType.RRI: [
                self.translate_register_argument,
                self.translate_register_argument,
                self.translate_immediate_argument,
            ],
            ArgsType.RR: [
                self.translate_register_argument,
                self.translate_register_argument,
            ],
            ArgsType.RI: [
                self.translate_register_argument,
                self.translate_immediate_argument,
            ],
        }[args_type]

    def translate_command(self) -> RawCommand:
        """Translates command (op + args)."""
        token = self.next()

        normalized_command = token.value.strip().upper()

        op = Op[normalized_command].value

        args = [
            arg_translator()
            for arg_translator in self.get_args_type_translator_list(op.args_type)
        ]

        result: RawCommand = [op.code]
        result += args

        return result

    def translate_string_literal(self) -> list[int]:
        """Translates string literal."""
        token = self.next()

        return [ord(c) for c in token.value]

    def translate_number_literal(self) -> int:
        """Translates number literal."""
        token = self.next()

        return int(token.value)

    def get_label_value(self) -> str:
        """Gets label value."""
        token = self.next()
        return token.value

    def translate(self) -> tuple[list[Command | int], int]:
        """Returns a program translated from a token list and a program start."""
        raw_program: list[RawCommand | int] = []

        labels: dict[str, int] = dict()
        start = 0

        token = self.peek()

        while self.pos < len(self.tokens):
            token = self.peek()

            match token.type:
                case TokenType.INSTRUCTION:
                    raw_program.append(self.translate_command())
                case TokenType.LABEL:
                    label = self.get_label_value()

                    if label in labels.keys():
                        print(f'label redefenition: {label}')
                        return [], start

                    labels[label] = len(raw_program)

                    if label == START_LABEL:
                        start = labels[label]
                case TokenType.LITERAL_STRING:
                    raw_program.extend(self.translate_string_literal())
                case TokenType.LITERAL_NUMBER:
                    raw_program.append(self.translate_number_literal())
                case _:
                    print(f'Unexpected token: {token}')
                    return [], start

        if START_LABEL not in labels.keys():
            print(f'no {START_LABEL} found!')
            return [], start

        program = resolve_labels_in_program(raw_program, labels)

        return program, start
