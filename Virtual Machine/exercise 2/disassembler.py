import sys

# Still TODO: prettier solution for OPS dictionary, check behavior for multiple loops

# later put in other doc or find prettier solution
OPS_CODE = {
    "01": {"op_name":"hlt", "fmt": "--"},  # Halt program
    "02": {"op_name":"ldc", "fmt": "rv"},  # Load value
    "03": {"op_name":"ldr", "fmt": "rr"},  # Load register
    "04": {"op_name":"cpy", "fmt": "rr"},  # Copy register
    "05": {"op_name":"str", "fmt": "rr"},  # Store register
    "06": {"op_name":"add", "fmt": "rr"},  # Add
    "07": {"op_name":"sub", "fmt": "rr"},  # Subtract
    "08": {"op_name":"beq", "fmt": "rv"},  # Branch if equal
    "09": {"op_name":"bne", "fmt": "rv"},  # Branch if not equal
    "0a": {"op_name":"prr", "fmt": "r-"},  # Print register
    "0b": {"op_name":"prm", "fmt": "r-"},  # Print memory
}




# Input: 3 byte long numbers in hexadecimal
# Output: write program in assembly into file


# I 03070a  fmt arg1 arg0 op
# O ldr R1 5 fmt: op arg0 arg1



# [class]
class Disassembler:
    def disassemble(self, lines):
        lines = self._get_lines(lines) # [123456 , 012345, 987654, ...]
        instructions = []
        labelnr = 1 # if we have multiple branches we want different labels unless
        labels_ip = set() # if we have multiple branches to the same place we want the same label

        for ln in lines: # for each line
            arg1, arg0, op_code = self._split(ln) # [12,34,56]
            op_dict = self._find_op(op_code) # {"op_name":"cpy", "fmt": "rr"}
            arg0, arg1 = self._find_args(op_dict, int(arg0,16), int(arg1,16)) # [R1, R2] format values
            if 8 <= int(op_code, 16) <= 9: # BNE BEQ controlflow instruction
                if int(arg1) not in labels_ip: 
                    label = "label" + str(labelnr)
                    labelnr = labelnr + 1
                    instructions.insert(int(arg1) + len(labels_ip), label + ":")
                    labels_ip.add(int(arg1))

                arg1 = "@" + label
            
            instructions.append((op_dict['op_name'] + " " + arg0 + " " + arg1).strip())    
        
        return instructions 
# [/class]

  
    def _split(self, line):
        return line[0:2],line[2:4],line[4:6].strip()
    
    def _find_op(self, op_code):
        return OPS_CODE[op_code]
    
    def _find_args(self, op_dict, in_arg0, in_arg1):
        # check args and based on operation give back the write thing
        # in: {"op_name":"cpy", "fmt": "rr"} 0a 01
        # out: ldc R1 3

        fmt = op_dict["fmt"]
        arg0 = ""
        arg1 = ""
        if fmt == "--":
            return arg0, arg1 

        arg0 =  'R' + str(in_arg0)
        
        if fmt == "rv":
            arg1 = str(in_arg1)
        elif fmt == "rr":
            arg1 = 'R' + str(in_arg1)
            
        return arg0, arg1

    def _get_lines(self, lines):
        lines = [ln.strip() for ln in lines]
        lines = [ln for ln in lines if len(ln) > 0]
        lines = [ln for ln in lines if not self._is_comment(ln)]
        return lines

    def _is_comment(self, line):
        return line.startswith("#")

def main(disassembler_cls):
    assert len(sys.argv) == 3, f"Usage: {sys.argv[0]} input|- output|-"
    reader = open(sys.argv[1], "r") if (sys.argv[1] != "-") else sys.stdin
    writer = open(sys.argv[2], "w") if (sys.argv[2] != "-") else sys.stdout

    lines = reader.readlines()
    disassembler = disassembler_cls()
    program = disassembler.disassemble(lines)
    for instruction in program:
        print(instruction, file=writer)

# is only called if this file is run (main)
if __name__ == "__main__":
    main(Disassembler)



