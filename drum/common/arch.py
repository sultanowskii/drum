from dataclasses import dataclass
from enum import Enum

from drum.common.util.error import Result
from drum.common.util.iota import Iota

ImmediateArgument = int
RegisterArgument = str
CommandArgument = ImmediateArgument | RegisterArgument


_register_iota = Iota()


@dataclass
class RegisterDef:
    """Register definition."""
    name: str
    code: int


class Register(Enum):
    """Register."""
    R0 = RegisterDef('R0', _register_iota())
    R1 = RegisterDef('R1', _register_iota())
    R2 = RegisterDef('R2', _register_iota())
    R3 = RegisterDef('R3', _register_iota())
    R4 = RegisterDef('R4', _register_iota())
    R5 = RegisterDef('R5', _register_iota())
    R6 = RegisterDef('R6', _register_iota())
    R7 = RegisterDef('R7', _register_iota())

    @staticmethod
    def get_register_by_name(name: str) -> Result['Register']:
        """Returns register with provided name. Error if it doesn't exist."""
        for reg in Register:
            if reg.value.name == name:
                return reg, None
        return Register.R0, f"register with name {name} doesn\'t exist"

    @staticmethod
    def get_register_by_code(code: int) -> Result['Register']:
        """Returns register with provided code. Error if it doesn't exist."""
        for reg in Register:
            if reg.value.code == code:
                return reg, None
        return Register.R0, f"register with code {code} doesn\'t exist"


class ArgsType(Enum):
    """Type of command argument list."""
    ZERO = ''
    RRR = 'RRR'
    RRI = 'RRI'
    RR = 'RR'
    RI = 'RI'


@dataclass
class OpDef:
    """Operation definition."""
    name: str
    args_type: ArgsType
    code: int


_op_iota = Iota()


class Op(Enum):
    """Operation."""
    NOP = OpDef('NOP', ArgsType.ZERO, _op_iota())

    ADD = OpDef('ADD', ArgsType.RRR, _op_iota())
    ADDI = OpDef('ADDI', ArgsType.RRI, _op_iota())
    SUB = OpDef('SUB', ArgsType.RRR, _op_iota())
    SUBI = OpDef('SUBI', ArgsType.RRI, _op_iota())
    MUL = OpDef('MUL', ArgsType.RRR, _op_iota())
    MULI = OpDef('MULI', ArgsType.RRI, _op_iota())
    DIV = OpDef('DIV', ArgsType.RRR, _op_iota())
    DIVI = OpDef('DIVI', ArgsType.RRI, _op_iota())
    REM = OpDef('REM', ArgsType.RRR, _op_iota())
    REMI = OpDef('REMI', ArgsType.RRI, _op_iota())
    XOR = OpDef('XOR', ArgsType.RRR, _op_iota())
    XORI = OpDef('XORI', ArgsType.RRI, _op_iota())

    ST = OpDef('ST', ArgsType.RR, _op_iota())
    STI = OpDef('STI', ArgsType.RI, _op_iota())

    LD = OpDef('LD', ArgsType.RR, _op_iota())
    LDI = OpDef('LDI', ArgsType.RI, _op_iota())

    BEQ = OpDef('BEQ', ArgsType.RRI, _op_iota())
    BNE = OpDef('BNE', ArgsType.RRI, _op_iota())
    BLT = OpDef('BLT', ArgsType.RRI, _op_iota())
    BLE = OpDef('BLE', ArgsType.RRI, _op_iota())
    BGT = OpDef('BGT', ArgsType.RRI, _op_iota())
    BGE = OpDef('BGE', ArgsType.RRI, _op_iota())
