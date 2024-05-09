from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """Type of lexed token."""
    LABEL = 'Label'
    LITERAL_STRING = 'String literal'
    LITERAL_NUMBER = 'Number literal'
    INSTRUCTION = 'Instruction'
    ARGUMENT_NUMBER = 'Number argument'
    ARGUMENT_STRING = 'String argument'
    ARGUMENT_LABEL = 'Label argument'
    ARGUMENT_REGISTER = 'Register argument'
    ERROR = 'Error'


@dataclass
class Token:
    """Lexed token."""
    value: str
    type: TokenType
