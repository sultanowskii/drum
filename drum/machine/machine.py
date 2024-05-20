from typing import Callable, Optional

from drum.common.arch import (
    BRANCH_OPS,
    CALC_OPS,
    CALC_RRI_OPS,
    CALC_RRR_OPS,
    HALT_OP,
    IO_OPS,
    MEMORY_OPS,
    MEMORY_RI_OPS,
    MEMORY_RR_OPS,
    Op,
    Program,
    Register,
    Word,
)

Buffer = list[int]
Memory = list[Word]
Value = int
ImmediateValue = int


class DataPath:
    input_buffer: Buffer
    output_buffer: Buffer
    data_address: int
    memory: Memory
    memory_capacity: int
    registers: dict[Register, Value]
    _truth: bool

    def __init__(
        self,
        memory_capacity: int,
        program: Program,
        input_buffer: Buffer = list(),
    ) -> None:
        self.input_buffer = input_buffer
        self.output_buffer = []
        self.data_address = 0
        self.memory_capacity = memory_capacity
        self.memory = program + [[0]] * (self.memory_capacity - len(program))
        self.registers = dict((
            (r, 0)
            for r in Register
        ))
        self._truth = False

    def _reg_value(self, reg: Register) -> int:
        return self.registers[reg]

    def _reg_value_or_imm(self, o: Register | ImmediateValue) -> int:
        if isinstance(o, Register):
            return self._reg_value(o)
        else:
            return o

    def truth(self) -> bool:
        return self._truth

    def signal_rd(
        self,
        destination: Register,
    ) -> None:
        value = self.memory[self.data_address]

        self.registers[destination] = value[0]

    def signal_rd_imm(
        self,
        destination: Register,
        imm: ImmediateValue,
    ) -> None:
        self.registers[destination] = imm

    def signal_wr(
        self,
        source: Register,
    ) -> None:
        value = self.registers[source]

        self.memory[self.data_address] = [value]

    def signal_wr_imm(
        self,
        imm: ImmediateValue,
    ) -> None:
        self.memory[self.data_address] = [imm]

    def signal_set_data_address(
        self,
        new: Register | ImmediateValue,
    ) -> None:
        addr = self._reg_value_or_imm(new)
        self.data_address = addr

    def signal_alu(
        self,
        left: Register,
        right: Register | ImmediateValue,
        op: Op,
        destination: Optional[Register] = None,
    ) -> None:
        left_value = self._reg_value(left)
        right_value = self._reg_value_or_imm(right)
        result = 0

        match op:
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
                self._truth = left_value == right_value
            case Op.BNE:
                self._truth = left_value != right_value
            case Op.BLT:
                self._truth = left_value < right_value
            case Op.BLE:
                self._truth = left_value <= right_value
            case Op.BGT:
                self._truth = left_value > right_value
            case Op.BGE:
                self._truth = left_value >= right_value

        print(left, right)
        if op in CALC_OPS:
            assert destination is not None
            self.registers[destination] = result


class ControlUnit:
    data_path: DataPath
    program: Program
    instruction_counter: int

    def __init__(self, data_path: DataPath, program: Program, start_addr: int = 0) -> None:
        self.data_path = data_path
        self.program = program
        self.instruction_counter = start_addr

    def set_instruction_counter(self, new: int | None = None) -> None:
        if new is None:
            self.instruction_counter += 1
        else:
            self.instruction_counter = new

    def execute_calc_rrr_op(self, op: Op, raw_args: list[int]) -> None:
        destination_reg, _err = Register.get_by_code(raw_args[0])
        left, _err = Register.get_by_code(raw_args[1])
        right, _err = Register.get_by_code(raw_args[2])
        self.data_path.signal_alu(left, right, op, destination_reg)

    def execute_calc_rri_op(self, op: Op, raw_args: list[int]) -> None:
        destination_reg, _err = Register.get_by_code(raw_args[0])
        left, _err = Register.get_by_code(raw_args[1])
        right = raw_args[2]
        self.data_path.signal_alu(left, right, op, destination_reg)

    def execute_calc_op(self, op: Op, raw_args: list[int]) -> None:
        execute: Callable[[Op, list[int]], None] = self.execute_error
        if op in CALC_RRR_OPS:
            execute = self.execute_calc_rrr_op
        elif op in CALC_RRI_OPS:
            execute = self.execute_calc_rri_op
        execute(op, raw_args)
        self.set_instruction_counter()

    def execute_memory_rr_op(self, op: Op, raw_args: list[int]) -> None:
        reg1, _err = Register.get_by_code(raw_args[0])
        reg2, _err = Register.get_by_code(raw_args[1])

        match op:
            case Op.LD:
                self.data_path.signal_set_data_address(reg1)
                self.data_path.signal_rd(reg2)
            case Op.ST:
                self.data_path.signal_set_data_address(reg1)
                self.data_path.signal_wr(reg2)

    def execute_memory_ri_op(self, op: Op, raw_args: list[int]) -> None:
        reg, _err = Register.get_by_code(raw_args[0])
        imm = raw_args[1]

        match op:
            case Op.LDI:
                self.data_path.signal_rd_imm(reg, imm)
            case Op.STI:
                self.data_path.signal_set_data_address(reg)
                self.data_path.signal_wr_imm(imm)

    def execute_memory_op(self, op: Op, raw_args: list[int]) -> None:
        execute: Callable[[Op, list[int]], None] = self.execute_error
        if op in MEMORY_RR_OPS:
            execute = self.execute_memory_rr_op
        elif op in MEMORY_RI_OPS:
            execute = self.execute_memory_ri_op
        execute(op, raw_args)
        self.set_instruction_counter()

    def execute_io_op(self, op: Op, raw_args: list[int]) -> None:
        pass

    def execute_branch_op(self, op: Op, raw_args: list[int]) -> None:
        left, _err = Register.get_by_code(raw_args[0])
        right, _err = Register.get_by_code(raw_args[1])
        addr = raw_args[2]

        self.data_path.signal_alu(left, right, op)

        if self.data_path.truth():
            self.set_instruction_counter(addr)

    def execute_error(self, _op: Op, _raw_args: list[int]) -> None:
        print('ERROR!!!')

    def decode_and_execute(self) -> bool:
        if self.instruction_counter >= len(self.program):
            return False

        raw = self.program[self.instruction_counter]
        raw_opcode = raw[0]
        raw_args = raw[1:]

        op, _err = Op.get_by_code(raw_opcode)

        execute: Callable[[Op, list[int]], None] = self.execute_error

        if op in CALC_OPS:
            execute = self.execute_calc_op
        elif op in MEMORY_OPS:
            execute = self.execute_memory_op
        elif op in IO_OPS:
            execute = self.execute_io_op
        elif op in BRANCH_OPS:
            execute = self.execute_branch_op
        elif op == HALT_OP:
            return False

        execute(op, raw_args)
        return True


def exec_program(program: Program, start_addr: int = 0, input_buffer: Buffer = list()) -> None:
    data_path = DataPath(20, program, input_buffer)
    control_unit = ControlUnit(data_path, data_path.memory, start_addr)

    while control_unit.decode_and_execute():
        print(control_unit.data_path.memory)
        for k, v in control_unit.data_path.registers.items():
            print(f'{k.value.name}: {v}')
        print(f'data_addr={control_unit.data_path.data_address}')
        print()
        pass
