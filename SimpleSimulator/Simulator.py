import sys

instructions_count = 0


class Memory:
    def __init__(self):
        self.memory = [0] * 128

    def read(self, address):
        return self.memory[address]

    def write(self, address, data):
        self.memory[address] = data

    def dump(self):
        ii = 0
        for data in self.memory:
            print(f"{data:016b}")

    def dumpOnlyVarMemory(self):
        # Variable are stored in memory after all instructions end.
        # Max instructions possible is 128. So variable memory
        # will start from 128
        for ii in range(128, 256):
            val = self.memory[ii]
            print(f"{val:016b}")


class RegisterFile:
    def __init__(self):
        self.registers = {
            '000': 0,
            '001': 0,
            '010': 0,
            '011': 0,
            '100': 0,
            '101': 0,
            '110': 0,
            'FLAGS': 0
        }

    def resetFlagsRegister(self):
        self.registers['FLAGS'] = 0

    def read(self, register):
        return self.registers[register]

    def write(self, register, data):
        self.registers[register] = data

    def dump(self):
        for register, value in self.registers.items():
            print(f"{register}: {value:016b}")

    def set_overflow_flag(self):
        self.registers['FLAGS'] |= 0b1000

    def unset_overflow_flag(self):
        self.registers['FLAGS'] &= 0b0111

    def get_overflow_flag(self):
        return self.registers['FLAGS'] & 0b1000

    def set_less_than_flag(self):
        self.registers['FLAGS'] |= 0b0100

    def unset_less_than_flag(self):
        self.registers['FLAGS'] &= 0b1011

    def get_less_than_flag(self):
        return self.registers['FLAGS'] & 0b0100

    def set_greater_than_flag(self):
        self.registers['FLAGS'] |= 0b0010

    def unset_greater_than_flag(self):
        self.registers['FLAGS'] &= 0b1101

    def get_greater_than_flag(self):
        return self.registers['FLAGS'] & 0b0010

    def set_equal_flag(self):
        self.registers['FLAGS'] |= 0b0001

    def unset_equal_flag(self):
        self.registers['FLAGS'] &= 0b1110

    def get_equal_flag(self):
        return self.registers['FLAGS'] & 0b0001


class ExecutionEngine:
    def __init__(self, memory, register_file, program_counter):
        self.memory = memory
        self.register_file = register_file
        self.program_counter = program_counter
        self.halted = False

    def execute(self, instruction):
        # Convert instruction to binary string representation
        instruction_str = bin(instruction)[2:].zfill(16)
        opcode = instruction_str[:5]

        if opcode == '00000':  # Addition
            # Type-A
            unused = instruction_str[5:7]
            reg1 = instruction_str[7:10]
            reg2 = instruction_str[10:13]
            reg3 = instruction_str[13:]

            value2 = self.register_file.read(reg2)
            value3 = self.register_file.read(reg3)
            result = value2 + value3

            if result > 0b1111111111111111:
                self.register_file.set_overflow_flag()
                self.register_file.write(reg1, 0)
            else:
                self.register_file.write(reg1, result)
                self.register_file.resetFlagsRegister()

        elif opcode == '00001':  # Subtraction
            # Type-A
            unused = instruction_str[5:7]
            reg1 = instruction_str[7:10]
            reg2 = instruction_str[10:13]
            reg3 = instruction_str[13:]

            value2 = self.register_file.read(reg2)
            value3 = self.register_file.read(reg3)

            if value2 < value3:
                self.register_file.set_overflow_flag()
                self.register_file.write(reg1, 0)
            else:
                result = value2 - value3
                self.register_file.write(reg1, result)
                self.register_file.resetFlagsRegister()

        elif opcode == '00010':  # Move Immediate
            # Type-B
            unused = instruction_str[5:6]
            reg1 = instruction_str[6:9]
            imm = instruction_str[9:]

            self.register_file.write(reg1, int(imm, 2))
            self.register_file.resetFlagsRegister()

        elif opcode == '00011':  # Move Register
            # Type-C
            unused = instruction_str[5:10]
            reg1 = instruction_str[10:13]
            reg2 = instruction_str[13:]
            if (int(reg2, 2) == 0b111):
                reg2 = 'FLAGS'

            value = self.register_file.read(reg2)
            self.register_file.write(reg1, value)
            self.register_file.resetFlagsRegister()

        elif opcode == '00100':  # Load
            # Type-D
            unused = instruction_str[5:6]
            reg1 = instruction_str[6:9]
            addressStr = instruction_str[9:]
            address = int(addressStr, 2)

            # Variable are stored in memory after all instructions end.
            # Max instructions possible is 128. So variable memory
            # will start from 128
            #address += 128

            # Changes to match official output
            address += instructions_count

            value = self.memory.read(address)
            self.register_file.write(reg1, value)
            self.register_file.resetFlagsRegister()

        elif opcode == '00101':  # Store
            # Type-D
            unused = instruction_str[5:6]
            reg1 = instruction_str[6:9]
            addressStr = instruction_str[9:]
            address = int(addressStr, 2)

            # Variable are stored in memory after all instructions end.
            # Max instructions possible is 128. So variable memory
            # will start from 128
            #address += 128

            # Changes to match official output
            address += instructions_count

            value = self.register_file.read(reg1)
            self.memory.write(address, value)
            self.register_file.resetFlagsRegister()

        elif opcode == '00110':  # Multiply
            # Type-A
            unused = instruction_str[5:7]
            reg1 = instruction_str[7:10]
            reg2 = instruction_str[10:13]
            reg3 = instruction_str[13:]

            value2 = self.register_file.read(reg2)
            value3 = self.register_file.read(reg3)
            result = value2 * value3

            if result > 0b1111111111111111:
                self.register_file.set_overflow_flag()
                self.register_file.write(reg1, 0)
            else:
                self.register_file.write(reg1, result)
                self.register_file.resetFlagsRegister()

        elif opcode == '00111':  # Divide
            # Type-C
            unused = instruction_str[5:10]
            reg3 = instruction_str[10:13]
            reg4 = instruction_str[13:]

            value3 = self.register_file.read(reg3)
            value4 = self.register_file.read(reg4)
            if value4 == 0:
                self.register_file.set_overflow_flag()
                self.register_file.write('000', 0)
                self.register_file.write('001', 0)
            else:
                quotient = value3 // value4
                remainder = value3 % value4
                self.register_file.write('000', quotient)
                self.register_file.write('001', remainder)
                self.register_file.resetFlagsRegister()

        elif opcode == '01000':  # Right shift
            # Type-B
            unused = instruction_str[5:6]
            reg1 = instruction_str[6:9]
            imm_str = instruction_str[9:]
            imm = int(imm_str, 2)

            value1 = self.register_file.read(reg1)
            result = value1 >> imm
            self.register_file.write(reg1, result)
            self.register_file.resetFlagsRegister()

        elif opcode == '01001':  # Left shift
            # Type-B
            unused = instruction_str[5:6]
            reg1 = instruction_str[6:9]
            imm_str = instruction_str[9:]
            imm = int(imm_str, 2)
            value1 = self.register_file.read(reg1)
            result = value1 << imm
            self.register_file.write(reg1, result)
            self.register_file.resetFlagsRegister()

        elif opcode == '01010':  # XOR
            # Type-A
            unused = instruction_str[5:7]
            reg1 = instruction_str[7:10]
            reg2 = instruction_str[10:13]
            reg3 = instruction_str[13:]

            value2 = self.register_file.read(reg2)
            value3 = self.register_file.read(reg3)
            result = value2 ^ value3
            self.register_file.write(reg1, result)
            self.register_file.resetFlagsRegister()

        elif opcode == '01011':  # OR
            # Type-A
            unused = instruction_str[5:7]
            reg1 = instruction_str[7:10]
            reg2 = instruction_str[10:13]
            reg3 = instruction_str[13:]

            value2 = self.register_file.read(reg2)
            value3 = self.register_file.read(reg3)
            result = value2 | value3
            self.register_file.write(reg1, result)
            self.register_file.resetFlagsRegister()

        elif opcode == '01100':  # AND
            # Type-A
            unused = instruction_str[5:7]
            reg1 = instruction_str[7:10]
            reg2 = instruction_str[10:13]
            reg3 = instruction_str[13:]

            value2 = self.register_file.read(reg2)
            value3 = self.register_file.read(reg3)
            result = value2 & value3
            self.register_file.write(reg1, result)
            self.register_file.resetFlagsRegister()

        elif opcode == '01101':  # Invert
            # Type-C
            unused = instruction_str[5:10]
            reg1 = instruction_str[10:13]
            reg2 = instruction_str[13:]

            value2 = self.register_file.read(reg2)
            result = ~value2 & 0b1111111111111111
            self.register_file.write(reg1, result)
            self.register_file.resetFlagsRegister()

        elif opcode == '01110':  # Compare
            # Type-C
            unused = instruction_str[5:10]
            reg1 = instruction_str[10:13]
            reg2 = instruction_str[13:]

            value1 = self.register_file.read(reg1)
            value2 = self.register_file.read(reg2)
            if value1 < value2:
                self.register_file.set_less_than_flag()
            elif value1 > value2:
                self.register_file.set_greater_than_flag()
            else:
                self.register_file.set_equal_flag()

        elif opcode == '01111':  # Unconditional Jump
            # Type-E
            unused = instruction_str[5:9]
            addressStr = instruction_str[9:]
            address = int(addressStr, 2)
            new_pc = address

            self.register_file.resetFlagsRegister()
            return False, new_pc

        elif opcode == '11100':  # Jump If Less Than
            # Type-E
            unused = instruction_str[5:9]
            addressStr = instruction_str[9:]
            address = int(addressStr, 2)

            flag = self.register_file.get_less_than_flag()
            self.register_file.resetFlagsRegister()
            if flag != 0:
                new_pc = address
                return False, new_pc

        elif opcode == '11101':  # Jump If Greater Than
            # Type-E
            unused = instruction_str[5:9]
            addressStr = instruction_str[9:]
            address = int(addressStr, 2)

            flag = self.register_file.get_greater_than_flag()
            self.register_file.resetFlagsRegister()
            if flag != 0:
                new_pc = address
                return False, new_pc

        elif opcode == '11111':  # Jump If Equal
            # Type-E
            unused = instruction_str[5:9]
            addressStr = instruction_str[9:]
            address = int(addressStr, 2)

            flag = self.register_file.get_equal_flag()
            self.register_file.resetFlagsRegister()
            if flag != 0:
                new_pc = address
                return False, new_pc

        elif opcode == '10010':  # Move Float
            # Type-B-Float
            #unused = instruction_str[5:6]
            reg1 = instruction_str[5:8]
            imm_str = instruction_str[8:]
            imm = bin(int(imm_str, 2))[2:]
            #self.register_file.write(reg1, imm)
            # self.register_file.resetFlagsRegister()

        elif opcode == '10000':  # Float Addition
            # Type-A
            unused = instruction_str[5:7]
            reg1 = instruction_str[7:10]
            reg2 = instruction_str[10:13]
            reg3 = instruction_str[13:]

            value2 = self.register_file.read(reg2)
            value3 = self.register_file.read(reg3)
            #float_val2 = binary_to_float16(str(value2))
            #float_val3 = binary_to_float16(str(value3))
            #float_result = float_val2 + float_val3
            # if abs(float_result) >= 2 ** (16 - 1):
            #    self.register_file.set_overflow_flag()
            #    self.register_file.write(reg1, 0)
            # else:
            #    #TBD
            #    #Fix add logic
            #    self.register_file.write(reg1, 0)
            #    self.register_file.resetFlagsRegister()

        elif opcode == '10001':  # Float Subtraction
            # Type-A
            unused = instruction_str[5:7]
            reg1 = instruction_str[7:10]
            reg2 = instruction_str[10:13]
            reg3 = instruction_str[13:]

            value2 = self.register_file.read(reg2)
            value3 = self.register_file.read(reg3)
            #float_val2 = binary_to_float16(str(value2))
            #float_val3 = binary_to_float16(str(value3))

            # if float_val3 > float_val2:
            #    self.register_file.set_overflow_flag()
            #    self.register_file.write(reg1, 0)
            # else:
            #    float_result = float_val2 - float_val3
            #    #TBD
            #    #Convert float_result to 16 bit
            #    self.register_file.write(reg1, 0)
            #    self.register_file.resetFlagsRegister()

        elif opcode == '10011':  # Set
            # Type-B
            unused = instruction_str[5:6]
            reg1 = instruction_str[6:9]
            imm_str = instruction_str[9:]
            imm = int(imm_str, 2)

            reg_val1 = self.register_file.read(reg1)
            mask_value = 0b1 << imm
            reg_val1 |= mask_value

            self.register_file.write(reg1, reg_val1)
            self.register_file.resetFlagsRegister()

        elif opcode == '10100':  # Clear
            # Type-B
            unused = instruction_str[5:6]
            reg1 = instruction_str[6:9]
            imm_str = instruction_str[9:]
            imm = int(imm_str, 2)

            reg_val1 = self.register_file.read(reg1)
            mask_value = 0b1 << imm
            invert_mask_value = ~mask_value & 0xFFFF
            reg_val1 &= invert_mask_value

            self.register_file.write(reg1, reg_val1)
            self.register_file.resetFlagsRegister()

        elif opcode == '10101':  # Toggle
            # Type-B
            unused = instruction_str[5:6]
            reg1 = instruction_str[6:9]
            imm_str = instruction_str[9:]
            imm = int(imm_str, 2)

            reg_val1 = self.register_file.read(reg1)
            mask_value = 0b1 << imm
            reg_val1 ^= mask_value

            self.register_file.write(reg1, reg_val1)
            self.register_file.resetFlagsRegister()

        elif opcode == '10110':  # Rotate Left
            # Type-B
            unused = instruction_str[5:6]
            reg1 = instruction_str[6:9]
            imm_str = instruction_str[9:]
            imm = int(imm_str, 2)

            reg_val1 = self.register_file.read(reg1)
            num1 = (reg_val1 << imm) & 0xFFFF
            num2 = (reg_val1 >> (16 - imm)) & 0xFFFF
            result = num1 | num2
            reg_val1 = result

            self.register_file.write(reg1, reg_val1)
            self.register_file.resetFlagsRegister()

        elif opcode == '10111':  # Rotate Right
            # Type-B
            unused = instruction_str[5:6]
            reg1 = instruction_str[6:9]
            imm_str = instruction_str[9:]
            imm = int(imm_str, 2)

            reg_val1 = self.register_file.read(reg1)
            num1 = (reg_val1 >> imm) & 0xFFFF
            num2 = (reg_val1 << (16 - imm)) & 0xFFFF
            result = num1 | num2
            reg_val1 = result

            self.register_file.write(reg1, reg_val1)
            self.register_file.resetFlagsRegister()

        elif opcode == '11010':  # Halt
            return True, None

        new_pc = self.program_counter + 1
        return False, new_pc


def binary_to_float16(binary_string):
    try:
        # Check if the binary string is 16 bits
        if len(binary_string) != 16:
            raise ValueError("Binary string must be 16 bits.")

        # Convert the binary string to an integer
        integer_value = int(binary_string, 2)

        # Check if the integer value is negative
        if integer_value >= 2 ** (16 - 1):
            integer_value -= 2 ** 16

        # Convert the integer to a float
        float_value = float(integer_value)

        return float_value

    except Exception as e:
        print("Error:", str(e))


def float_to_binary_16bit(floating_number):
    try:
        # Convert the string to a floating-point number
        number = float(floating_number)

        # Check if the number can fit into an 8-bit register
        if abs(number) >= 2 ** (16 - 1):
            raise Exception(
                "Number is too large to fit in an 16-bit register.")

        # Convert the number to a binary string with 8 bits
        binary_string = format(int(number), '016b')

        return binary_string

    except Exception as e:
        print("Error:", str(e))


def initialize_memory_from_raw_bin(memory, raw_bin_instructions):
    for i, instruction in enumerate(raw_bin_instructions):
        instruction = instruction.strip()
        if instruction:
            try:
                int_val = int(instruction, 2)
                memory.write(i, int_val)
            except ValueError:
                print(f"Invalid instruction at line {i + 1}: {instruction}")
                exit(1)


def scan_input():  # Take input from file
    line_no = 0
    raw_bin = []   # removed empty lines
    while 1:
        try:
            line = input()+' '
            line_no += 1
            if line.isspace():
                continue
            raw_bin.append(line)
        except Exception:
            break
    return raw_bin


def simulator():
    memory = Memory()
    register_file = RegisterFile()
    program_counter = 0

    raw_bin_instructions = scan_input()
    instructions_count = len(raw_bin_instructions)

    execution_engine = ExecutionEngine(memory, register_file, program_counter)

    initialize_memory_from_raw_bin(memory, raw_bin_instructions)

    while not execution_engine.halted:

        instruction = memory.read(execution_engine.program_counter)
        execution_engine.halted, new_pc = execution_engine.execute(instruction)

        print(f"{execution_engine.program_counter:07b}        "
              f"{register_file.read('000'):016b} {register_file.read('001'):016b} "
              f"{register_file.read('010'):016b} {register_file.read('011'):016b} "
              f"{register_file.read('100'):016b} {register_file.read('101'):016b} "
              f"{register_file.read('110'):016b} {register_file.read('FLAGS'):016b}")

        execution_engine.program_counter = new_pc

    memory.dump()


if __name__ == '__main__':
    simulator()
