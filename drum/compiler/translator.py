from dataclasses import dataclass
from typing import Callable

from drum.common.arch import ArgsType, Op, Register
from drum.common.util.error import Result
from drum.compiler.tokens import Token, TokenType

Command = list[int]
RawCommand = list[int | str]
Program = list[Command | int]
RawProgram = list[RawCommand | int]

ImmediateArgument = int
RegisterArgument = str
LabelReferenceArgument = str
Argument = ImmediateArgument | RegisterArgument | LabelReferenceArgument

START_LABEL = '_start'


@dataclass
class Executable:
    """Executable representation"""
    start: int
    program: Program


DUMMY_EXECUTABLE = Executable(0, [])


def resolve_labels_in_command(
    raw_command: RawCommand,
    labels: dict[str, int],
) -> Result[Command]:
    """Returns command with resolved label references."""
    command = []

    for line in raw_command:
        if isinstance(line, int):
            command.append(line)
            continue

        if line not in labels.keys():
            return [], f'undefined label: {line}'

        command.append(labels[line])

    return command, None


def resolve_labels_in_program(raw: RawProgram, labels: dict[str, int]) -> Result[Program]:
    """Resolves all label references in raw program - and returns the resulting one."""
    program: Program = []

    for line in raw:
        if isinstance(line, list):
            command, error = resolve_labels_in_command(line, labels)
            if error is not None:
                return program, error
            program.append(command)
        else:
            program.append(line)

    return program, None


class Translator:
    """Token to code translator."""

    pos: int
    tokens: list[Token]

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def next(self) -> Token:
        """Goes to the next token, returns current."""
        value = self.tokens[self.pos]
        self.pos += 1
        return value

    def go_back(self) -> None:
        """Goes back by one token."""
        self.pos -= 1

    def is_end(self) -> bool:
        """Checks if more tokens are available."""
        return self.pos < len(self.tokens)

    def peek(self) -> Token:
        """Returns the next token without consumption."""
        value = self.next()
        self.go_back()
        return value

    def translate_register_argument(self) -> Result[Argument]:
        """Translates register argument."""
        token = self.next()
        if token.type != TokenType.ARGUMENT_REGISTER:
            return 0, f'register argument expected, {token.value} found instead ({token.type})'

        register_name = token.value

        register, error = Register.get_by_name(register_name)
        if error is not None:
            return 0, f'invalid register: {register_name}'

        return register.value.code, None

    def translate_immediate_argument(self) -> Result[Argument]:
        """Translates immediate argument."""
        token = self.next()
        match token.type:
            case TokenType.ARGUMENT_NUMBER:
                try:
                    return int(token.value), None
                except ValueError:
                    return 0, f'invalid immediate argument: {token.value}'
            case TokenType.ARGUMENT_LABEL:
                return token.value, None
            case _:
                return 0, f'immediate argument expected, {token.value} found instead ({token.type})'

    def get_args_type_translator_list(
        self,
        args_type: ArgsType,
    ) -> list[Callable[[], Result[Argument]]]:
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

    def translate_command(self) -> Result[RawCommand]:
        """Translates command (op + args)."""
        token = self.next()
        if token.type != TokenType.INSTRUCTION:
            return [], f'instruction expected, {token.value} found instead ({token.type})'

        op, error = Op.get_by_name(token.value)
        if error is not None:
            return [], error

        op_def = op.value

        args = []

        for arg_translator in self.get_args_type_translator_list(op_def.args_type):
            arg, error = arg_translator()
            if error is not None:
                return [], error
            args.append(arg)

        result: RawCommand = [op_def.code]
        result += args

        return result, None

    def translate_string_literal(self) -> Result[list[int]]:
        """Translates string literal."""
        token = self.next()
        if token.type != TokenType.LITERAL_STRING:
            return [], f'string literal expected, {token.value} found instead ({token.type})'

        return [ord(c) for c in token.value], None

    def translate_number_literal(self) -> Result[int]:
        """Translates number literal."""
        token = self.next()
        if token.type != TokenType.LITERAL_NUMBER:
            return 0, f'number literal expected, {token.value} found instead ({token.type})'

        try:
            return int(token.value), None
        except ValueError:
            return 0, f'invalid number literal: {token.value}'

    def get_label_value(self) -> str:
        """Gets label value."""
        token = self.next()
        return token.value

    def translate(self) -> Result[Executable]:
        """Returns a program translated from a token list and a program start."""
        raw_program: RawProgram = []

        labels: dict[str, int] = dict()
        start = 0

        token = self.peek()

        while self.pos < len(self.tokens):
            token = self.peek()

            match token.type:
                case TokenType.INSTRUCTION:
                    command, error = self.translate_command()
                    if error is not None:
                        return DUMMY_EXECUTABLE, f'command parse error: {error}'
                    raw_program.append(command)
                case TokenType.LABEL:
                    label = self.get_label_value()

                    if label in labels.keys():
                        return DUMMY_EXECUTABLE, f'label redefenition: {label}'

                    labels[label] = len(raw_program)

                    if label == START_LABEL:
                        start = labels[label]
                case TokenType.LITERAL_STRING:
                    string, error = self.translate_string_literal()
                    if error is not None:
                        return DUMMY_EXECUTABLE, error

                    raw_program.extend(string)
                case TokenType.LITERAL_NUMBER:
                    number, error = self.translate_number_literal()
                    if error is not None:
                        return DUMMY_EXECUTABLE, error

                    raw_program.append(number)
                case _:
                    return DUMMY_EXECUTABLE, f'unexpected token on a top-level: {token}'

        if START_LABEL not in labels.keys():
            return DUMMY_EXECUTABLE, f'start label ({START_LABEL}) not found'

        program, error = resolve_labels_in_program(raw_program, labels)

        if error is not None:
            return DUMMY_EXECUTABLE, f'label resolution error: {error}'

        return Executable(start, program), None
