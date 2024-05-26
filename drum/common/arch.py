from dataclasses import dataclass
from enum import Enum

from drum.util.error import Result
from drum.util.iota import Iota

Command = list[int]
DataWord = list[int]
Word = Command | DataWord
Program = list[Word]

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
    def get_by_name(name: str) -> Result['Register']:
        """Returns register with provided name. Error if it doesn't exist."""
        sanitized_name = name.upper()

        for reg in Register:
            if reg.value.name == sanitized_name:
                return reg, None

        return Register.R0, f"register with name {name} doesn\'t exist"

    @staticmethod
    def get_by_code(code: int) -> Result['Register']:
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
    R = 'R'


@dataclass
class OpDef:
    """Operation definition."""
    name: str
    args_type: ArgsType
    code: int


_op_iota = Iota(0)


class Op(Enum):
    """Operation."""
    HLT = OpDef('HLT', ArgsType.ZERO, _op_iota())

    ADD = OpDef('ADD', ArgsType.RRR, _op_iota())
    ADDI = OpDef('ADDI', ArgsType.RRI, _op_iota())
    SUB = OpDef('SUB', ArgsType.RRR, _op_iota())
    SUBI = OpDef('SUBI', ArgsType.RRI, _op_iota())
    SHR = OpDef('SHR', ArgsType.RRR, _op_iota())
    SHRI = OpDef('SHRI', ArgsType.RRI, _op_iota())
    XOR = OpDef('XOR', ArgsType.RRR, _op_iota())
    XORI = OpDef('XORI', ArgsType.RRI, _op_iota())

    ST = OpDef('ST', ArgsType.RR, _op_iota())
    LD = OpDef('LD', ArgsType.RR, _op_iota())

    IN = OpDef('IN', ArgsType.R, _op_iota())
    OUT = OpDef('OUT', ArgsType.R, _op_iota())

    BEQ = OpDef('BEQ', ArgsType.RRI, _op_iota())
    BNE = OpDef('BNE', ArgsType.RRI, _op_iota())
    BLT = OpDef('BLT', ArgsType.RRI, _op_iota())
    BLE = OpDef('BLE', ArgsType.RRI, _op_iota())
    BGT = OpDef('BGT', ArgsType.RRI, _op_iota())
    BGE = OpDef('BGE', ArgsType.RRI, _op_iota())

    @staticmethod
    def get_by_name(name: str) -> Result['Op']:
        """Returns op with provided name. Error if it doesn't exist."""
        sanitized_name = name.upper()

        for op in Op:
            if op.value.name == sanitized_name:
                return op, None

        return Op.HLT, f"op with name {name} doesn\'t exist"

    @staticmethod
    def get_by_code(code: int) -> Result['Op']:
        """Returns op with provided code. Error if it doesn't exist."""
        for op in Op:
            if op.value.code == code:
                return op, None

        return Op.HLT, f"op with code {code} doesn\'t exist"


CALC_RRR_OPS = (
    Op.ADD,
    Op.SUB,
    Op.SHR,
    Op.XOR,
)

CALC_RRI_OPS = (
    Op.ADDI,
    Op.SUBI,
    Op.SHRI,
    Op.XORI,
)

CALC_OPS = CALC_RRR_OPS + CALC_RRI_OPS

MEMORY_OPS = (
    Op.ST,
    Op.LD,
)

IO_OPS = (
    Op.IN,
    Op.OUT,
)

BRANCH_OPS = (
    Op.BEQ,
    Op.BNE,
    Op.BLT,
    Op.BLE,
    Op.BGT,
    Op.BGE,
)

HALT_OP = Op.HLT
