from typing import Callable

from drum.common.arch import ArgsType, Command, Op, Register
from drum.util.error import Result


def fmt_reg(raw: int) -> Result[str]:
    """Returns a formatted register."""
    reg, err = Register.get_by_code(raw)
    if err is not None:
        return '', err

    return f'%{reg.value.name}', None


def fmt_imm(raw: int) -> Result[str]:
    """Returns a formatted immediate value."""
    return f'{raw}', None


ARGS_FMT: dict[ArgsType, list[Callable[[int], Result[str]]]] = {
    ArgsType.RRR: [
        fmt_reg,
        fmt_reg,
        fmt_reg,
    ],
    ArgsType.RRI: [
        fmt_reg,
        fmt_reg,
        fmt_imm,
    ],
    ArgsType.RR: [
        fmt_reg,
        fmt_reg,
    ],
    ArgsType.R: [
        fmt_reg,
    ],
    ArgsType.ZERO: [],
}


def fmt_instruction(raw: Command) -> Result[str]:
    """Returns a formatted instruction."""
    raw_op = raw[0]
    raw_args = raw[1:]

    op, err = Op.get_by_code(raw_op)
    if err is not None:
        return '', err

    s = f'{op.value.name}'

    args_fmt = ARGS_FMT[op.value.args_type]

    expected_argument_count = len(args_fmt)
    actual_argument_count = len(raw_args)
    if actual_argument_count != expected_argument_count:
        return '', (
            f'unexpected number of arguments: expected '
            f'{expected_argument_count}, got {actual_argument_count}'
        )

    formatted_args = []
    for raw_arg, fmt in zip(raw_args, args_fmt):
        formatted_arg, err = fmt(raw_arg)
        if err is not None:
            return '', err
        formatted_args.append(formatted_arg)

    if len(formatted_args) > 0:
        s += f' {", ".join(formatted_args)}'

    return s, None
