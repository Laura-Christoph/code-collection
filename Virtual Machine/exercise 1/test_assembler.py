from assembler import Assembler
import pytest

assembler = Assembler()

def get_assembler_result(inputFilename, outputFilename):
    with open(inputFilename, "r") as f:        
        res = assembler.assemble(f.readlines())
        with open(outputFilename, "w") as f:
            for line in res:
                print(line, file=f)

@pytest.mark.parametrize("op", ["hlt", "ldc", "ldr", "cpy", "str", "add", "sub", "beq", "bne", "prr", "prm", "count_up"])
def test_assembler_class(op):
    get_assembler_result(f"{op}.as", f"res_{op}.mx")
    with open(f"res_{op}.mx", "r") as res, open(f"exp_{op}.mx", "r") as exp:
        assert res.read() == exp.read()
