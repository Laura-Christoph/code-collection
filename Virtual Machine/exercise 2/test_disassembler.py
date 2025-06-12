from disassembler import Disassembler
import pytest

disassembler = Disassembler()

def get_disassembler_result(inputFilename, outputFilename):
    with open(inputFilename, "r") as f:        
        res = disassembler.disassemble(f.readlines())
        with open(outputFilename, "w") as f:
            for line in res:
                print(line, file=f)

@pytest.mark.parametrize("op", ["hlt", "ldc", "ldr", "cpy", "str", "add", "sub", "beq", "bne", "prr", "prm", "count_up"])
def test_disassembler_class(op):
    get_disassembler_result(f"{op}.mx", f"res_{op}.as")
    with open(f"res_{op}.as", "r") as res, open(f"exp_{op}.as", "r") as exp:
        assert res.read() == exp.read()