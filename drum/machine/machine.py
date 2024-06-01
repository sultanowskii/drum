from enum import Enum
from logging import getLogger
from queue import Queue
from typing import Callable, Iterable, Optional

from drum.common.arch import (
    BRANCH_OPS,
    CALC_OPS,
    CALC_RRI_OPS,
    CALC_RRR_OPS,
    HALT_OP,
    IO_OPS,
    MEMORY_OPS,
    Op,
    Program,
    Register,
    Word,
)
from drum.common.fmt import fmt_instruction
from drum.machine.io import OutputFormat
from drum.util.error import Error

logger = getLogger('machine')

Value = int
ImmediateValue = int


class SelRegValueSource(Enum):
    """Select register value source."""
    ALU = 'ALU_RESULT'
    INPUT = 'INPUT'
    MEM = 'MEM'


class DataPath:
    """DataPath."""
    # Input (io) buffer
    input_buffer: Queue[int]
    # Output (io) buffer
    output_buffer: Queue[int]
    # Memory address (pseudoregister)
    data_address: int
    # Result of ALU (pseudoregister)
    alu_result: int
    # Memory
    memory: list[Word]
    # Memory capacity
    memory_capacity: int
    # General register
    registers: dict[Register, Value]
    # Zero flag (used for conditional branching)
    _zero: bool

    def __init__(
        self,
        memory_capacity: int,
        program: Program,
        input_data: Iterable[int] = list(),
    ) -> None:
        self.input_buffer = Queue()
        for item in input_data:
            self.input_buffer.put(item)
        self.output_buffer = Queue()
        self.data_address = 0
        self.alu_result = 0
        self.memory_capacity = memory_capacity
        self.memory = program + [[0]] * (self.memory_capacity - len(program))
        self.registers = dict((
            (r, 0)
            for r in Register
        ))
        self._zero = False

    def _reg_value(self, reg: Register) -> int:
        """Get value of register."""
        return self.registers[reg]

    def _reg_value_or_imm(self, o: Register | ImmediateValue) -> int:
        """Get value of register or immediate value."""
        if isinstance(o, Register):
            return self._reg_value(o)
        return o

    def _set_reg_value(self, reg: Register, value: int) -> None:
        """Set value to register."""
        self.registers[reg] = value

    def _read_from_memory(self) -> int:
        """Get word from memory."""
        return self.memory[self.data_address][0]

    def _write_to_memory(self, value: int) -> None:
        """Set word in memory."""
        self.memory[self.data_address] = [value]

    def _in(self) -> int:
        """Receive byte from input."""
        return self.input_buffer.get()

    def _out(self, value: int) -> None:
        """Send byte to input."""
        self.output_buffer.put(value)

    def zero(self) -> bool:
        """Get zero value."""
        return self._zero

    def signal_latch_data_address(self, sel: Register) -> None:
        """Latches data address (based on selector)."""
        self.data_address = self._reg_value(sel)

    def signal_latch_mem_wr(self, sel_mem_wr_reg: Register) -> None:
        """Latches memory cell with value from register (chosen by selector)."""
        value = self._reg_value(sel_mem_wr_reg)
        self._write_to_memory(value)
        logger.debug(f'[{self.data_address}] = {value} ({repr(chr(value))})')

    def signal_output(self, sel_out_reg: Register) -> None:
        """Sends byte to output from register (chosen by selector)."""
        value = self._reg_value(sel_out_reg) & 0xff
        self.output_buffer.put(value)
        logger.debug(f'sent to output: {value} ({repr(chr(value))})')

    def signal_latch_register(
        self,
        sel_value_src: SelRegValueSource,
        reg: Optional[Register] = None,
        alu_ctl: Optional[Op] = None,
        sel_left: Optional[Register] = None,
        sel_right: Optional[Register | ImmediateValue] = None,
    ) -> None:
        """
        Latches register value.

        - register is chosen by sel_reg
        - source of value is chosen by sel_reg_value_src

        ALU: value is calculated by ALU
        MEM: value is taken from memory cell
        INPUT: byte value is taken from input
        """
        match sel_value_src:
            case SelRegValueSource.ALU:
                assert sel_left is not None
                assert sel_right is not None
                assert alu_ctl is not None

                left_value = self._reg_value(sel_left)
                right_value = self._reg_value_or_imm(sel_right)
                result = 0

                match alu_ctl:
                    case Op.ADD | Op.ADDI:
                        result = left_value + right_value
                    case Op.SUB | Op.SUBI:
                        result = left_value - right_value
                    case Op.SHR | Op.SHRI:
                        result = left_value >> right_value
                    case Op.SHR | Op.SHRI:
                        result = left_value >> right_value
                    case Op.XOR | Op.XORI:
                        result = left_value ^ right_value
                    case Op.BEQ:
                        self._zero = left_value == right_value
                    case Op.BNE:
                        self._zero = left_value != right_value
                    case Op.BLT:
                        self._zero = left_value < right_value
                    case Op.BLE:
                        self._zero = left_value <= right_value
                    case Op.BGT:
                        self._zero = left_value > right_value
                    case Op.BGE:
                        self._zero = left_value >= right_value

                if alu_ctl not in BRANCH_OPS:
                    assert reg is not None
                    self._set_reg_value(reg, result)
            case SelRegValueSource.INPUT:
                assert reg is not None
                value = self.input_buffer.get()
                self._set_reg_value(reg, value)
            case SelRegValueSource.MEM:
                assert reg is not None
                value = self._read_from_memory()
                self._set_reg_value(reg, value)


class ControlUnit:
    """Control Unit."""
    # Underlying data path
    data_path: DataPath
    # Program memory (should point to the same as data_path.memory)
    program: Program
    # Instruction pointer / program counter
    instruction_pointer: int
    # Inner executed instruction counter
    _counter: int
    # Inner tick
    _tick: int

    def __init__(self, data_path: DataPath, program: Program, start_addr: int = 0) -> None:
        self.data_path = data_path
        self.program = program
        self.instruction_pointer = start_addr
        self._counter = 0
        self._tick = 0

    def counter(self) -> int:
        """Gets current counter value."""
        return self._counter

    def counter_inc(self) -> int:
        """Increments counter value."""
        tmp = self._counter
        self._counter += 1
        return tmp

    def tick(self) -> int:
        """Gets current tick value."""
        return self._tick

    def tick_inc(self) -> int:
        """Increments tick value."""
        tmp = self._tick
        self._tick += 1
        return tmp

    def set_instruction_pointer(self, new: int | None = None) -> None:
        """
        Sets instruction pointer to value.

        If value is not provided, incremented.
        """
        if new is None:
            self.instruction_pointer += 1
        else:
            self.instruction_pointer = new

    def execute_arithmetic_rrr_op(self, op: Op, raw_args: list[int]) -> Error:
        """Executes arithmetic RRR operation."""
        destination_reg, err = Register.get_by_code(raw_args[0])
        if err is not None:
            return err

        left, err = Register.get_by_code(raw_args[1])
        if err is not None:
            return err

        right, err = Register.get_by_code(raw_args[2])
        if err is not None:
            return err

        self.data_path.signal_latch_register(
            SelRegValueSource.ALU,
            reg=destination_reg,
            alu_ctl=op,
            sel_left=left,
            sel_right=right,
        )
        self.tick_inc()

        return None

    def execute_arithmetic_rri_op(self, op: Op, raw_args: list[int]) -> Error:
        """Executes arithmetic RRI operation."""
        destination_reg, err = Register.get_by_code(raw_args[0])
        if err is not None:
            return err

        left, err = Register.get_by_code(raw_args[1])
        if err is not None:
            return err

        right = raw_args[2]
        self.data_path.signal_latch_register(
            SelRegValueSource.ALU,
            reg=destination_reg,
            alu_ctl=op,
            sel_left=left,
            sel_right=right,
        )
        self.tick_inc()

        return None

    def execute_arithmetic_op(self, op: Op, raw_args: list[int]) -> Error:
        """Executes arithmetic operation."""
        execute: Callable[[Op, list[int]], Error] = self.execute_dummy
        if op in CALC_RRR_OPS:
            execute = self.execute_arithmetic_rrr_op
        elif op in CALC_RRI_OPS:
            execute = self.execute_arithmetic_rri_op
        else:
            return 'programming error: no match in execute_arithmetic_op()'

        err = execute(op, raw_args)
        if err is not None:
            return err

        self.set_instruction_pointer()

        return None

    def execute_memory_op(self, op: Op, raw_args: list[int]) -> Error:
        """Executes memory operation."""
        reg1, err = Register.get_by_code(raw_args[0])
        if err is not None:
            return err

        reg2, err = Register.get_by_code(raw_args[1])
        if err is not None:
            return err

        match op:
            case Op.LD:
                self.data_path.signal_latch_data_address(reg2)
                self.tick_inc()

                self.data_path.signal_latch_register(SelRegValueSource.MEM, reg1)
                self.tick_inc()
            case Op.ST:
                self.data_path.signal_latch_data_address(reg2)
                self.tick_inc()

                self.data_path.signal_latch_mem_wr(reg1)
                self.tick_inc()
            case _:
                return 'programming error: no match in execute_memory_op()'

        self.set_instruction_pointer()

        return None

    def execute_io_op(self, op: Op, raw_args: list[int]) -> Error:
        """Executes IO operation."""
        reg, err = Register.get_by_code(raw_args[0])
        if err is not None:
            return err

        match op:
            case Op.IN:
                self.data_path.signal_latch_register(SelRegValueSource.INPUT, reg)
                self.tick_inc()
            case Op.OUT:
                self.data_path.signal_output(reg)
                self.tick_inc()
            case _:
                return 'programming error: no match in execute_io_op()'

        self.set_instruction_pointer()

        return None

    def execute_branch_op(self, op: Op, raw_args: list[int]) -> Error:
        """Executes branching operation."""
        left, err = Register.get_by_code(raw_args[0])
        if err is not None:
            return err

        right, err = Register.get_by_code(raw_args[1])
        if err is not None:
            return err

        addr = raw_args[2]

        self.data_path.signal_latch_register(
            SelRegValueSource.ALU,
            alu_ctl=op,
            sel_left=left,
            sel_right=right,
        )
        self.tick_inc()

        if self.data_path.zero():
            self.set_instruction_pointer(addr)
            return None

        self.set_instruction_pointer()
        return None

    def execute_dummy(self, _op: Op, _raw_args: list[int]) -> Error:
        return None

    def decode_and_execute(self) -> bool:
        """Decodes and executes instruction."""
        if self.instruction_pointer >= len(self.program):
            return False

        raw = self.program[self.instruction_pointer]
        raw_opcode = raw[0]
        raw_args = raw[1:]

        op, err = Op.get_by_code(raw_opcode)
        if err is not None:
            logger.error(err)
            return False

        execute: Callable[[Op, list[int]], Error] = self.execute_dummy

        if op in CALC_OPS:
            execute = self.execute_arithmetic_op
        elif op in MEMORY_OPS:
            execute = self.execute_memory_op
        elif op in IO_OPS:
            execute = self.execute_io_op
        elif op in BRANCH_OPS:
            execute = self.execute_branch_op
        elif op == HALT_OP:
            return False
        else:
            logger.fatal('programming error: unexpected valid op')
            return False

        err = execute(op, raw_args)
        if err is not None:
            logger.error(err)
            return False

        self.counter_inc()

        return True

    def get_state_string(self) -> str:
        """Returns current state in string format."""
        s = f'TICK={self.tick():4} '
        s += f'IP={self.instruction_pointer:3} '
        s += f'ADDR={self.data_path.data_address:3} '
        s += f'MEM={self.data_path._read_from_memory():6} '

        for reg, value in self.data_path.registers.items():
            s += f'{reg.value.name}={value:4} '

        instr = self.program[self.instruction_pointer]

        formatted_instruction, err = fmt_instruction(instr)
        if err is not None:
            logger.error('error while preparing state string: ' + err)

        s += formatted_instruction

        return s


def exec_program(
    program: Program,
    output_format: OutputFormat,
    start: int = 0,
    input_data: Iterable[int] = list(),
) -> str:
    """Executes a program. Returns formatted output."""
    data_path = DataPath(len(program) * 5, program, input_data)
    control_unit = ControlUnit(data_path, data_path.memory, start)

    logger.debug(control_unit.get_state_string())

    while control_unit.decode_and_execute():
        logger.debug(control_unit.get_state_string())

    logger.info(f'{control_unit.counter()} instructions executed')

    output_data = []
    while not control_unit.data_path.output_buffer.empty():
        output_data.append(control_unit.data_path.output_buffer.get())

    formatted_output = output_format.value.fmt_output_data(output_data)

    logger.info(f'Output: {formatted_output}')

    return formatted_output
