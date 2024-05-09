from dataclasses import dataclass
from enum import Enum

from drum.common.util.iota import Iota

ImmediateArgument = int
RegisterArgument = str
CommandArgument = ImmediateArgument | RegisterArgument


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


@dataclass
class Command:
    """Command (operation + its arguments)."""
    op: Op
    args: list[CommandArgument]
