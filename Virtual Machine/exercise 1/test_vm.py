from assembler import Assembler
from vm import VirtualMachine
import pytest

assembler = Assembler()
vm = VirtualMachine()

def get_vm_result(inputFilename, outputFilename):
    with open(inputFilename, "r") as f:        
        lines = [ln.strip() for ln in f.readlines()]
        program = [int(ln, 16) for ln in lines if ln]
        vm.initialize(program)
        vm.run()
        with open(outputFilename, "w") as f:
            vm.show(f)

@pytest.mark.parametrize("op", ["hlt", "ldc", "ldr", "cpy", "str", "add", "sub", "beq", "bne", "prr", "prm", "count_up"])
def test_vm_class(op):
    get_vm_result(f"exp_{op}.mx", f"vm_res_{op}.txt")
    with open(f"vm_res_{op}.txt", "r") as res, open(f"vm_exp_{op}.txt", "r") as exp:
        assert res.read() == exp.read()

def test_vm_memory_error():
    with open("exp_memory_error.mx", "w") as f:
        pass
    with open("exp_memory_error.mx", "a") as f:
        for i in range(256):
            f.write("000002\n")
        f.write("000001\n")
    with pytest.raises(Exception) as e_info:
        get_vm_result("exp_memory_error.mx", "res_memory_error.txt")
    assert e_info.value.args[0] == "Program too long"

def test_vm_op_not_found():
    invalid_op = "000033"
    with open("exp_invalid_op.mx", "w") as f:
        pass
    with open("exp_invalid_op.mx", "a") as f:
        f.write(f"{invalid_op}\n")
    with pytest.raises(Exception) as e_info:
        get_vm_result("exp_invalid_op.mx", "res_invalid_op.txt")
    assert e_info.value.args[0] == f"Unknown op {invalid_op}"
