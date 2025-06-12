import sys

from architecture import OPS, VMState
from vm_extend import VirtualMachineExtend


class VirtualMachineBreak(VirtualMachineExtend):
    # [init]
    def __init__(self):
        super().__init__()
        self.breaks = {}
        self.handlers |= {
            "b": self._do_add_breakpoint,
            "break": self._do_add_breakpoint,
            "c": self._do_clear_breakpoint,
            "clear": self._do_clear_breakpoint,
        }
    # [/init]

    # [show]
    def show(self):
        super().show()
        if self.breaks:
            self.write("-" * 6)
            for key, instruction in self.breaks.items():
                self.write(f"{key:06x}: {self.disassemble(key, instruction)}")
    # [/show]

    # [run]
    def run(self):
        self.state = VMState.STEPPING
        while self.state != VMState.FINISHED:
            instruction = self.ram[self.ip]
            op, arg0, arg1 = self.decode(instruction)

            if op == OPS["brk"]["code"]:
                original = self.breaks[self.ip]
                op, arg0, arg1 = self.decode(original)
                self.interact(self.ip)
                self.ip += 1
                self.execute(op, arg0, arg1)

            else:
                if self.state == VMState.STEPPING:
                    self.interact(self.ip)
                self.ip += 1
                self.execute(op, arg0, arg1)
    # [/run]

    # [add]
    def _do_add_breakpoint(self, addr):
        if self.ram[addr] == OPS["brk"]["code"]:
            return
        self.breaks[addr] = self.ram[addr]
        self.ram[addr] = OPS["brk"]["code"]
        return True
    # [/add]

    # [clear]
    def _do_clear_breakpoint(self, addr):
        if self.ram[addr] != OPS["brk"]["code"]:
            return
        self.ram[addr] = self.breaks[addr]
        del self.breaks[addr]
        return True
    # [/clear]

    def do_break(self, args):
        if len(args) == 1:
            address = int(args[0], 16)
            self._do_add_breakpoint(address)
            print(f"Breakpoint set at address {address:04x}")
        else:
            print("Invalid number of arguments. Usage: break <address>")


    def do_clear(self, args):
        if len(args) == 1:
            address = int(args[0], 16)
            self._do_clear_breakpoint(address)
            print(f"Breakpoint cleared at address {address:04x}")
        else:
            print("Invalid number of arguments. Usage: clear <address>")

    # [watch]
    def _do_add_watchpoint(self, addr):
        self.set_watchpoint(addr)
        return True

    def _do_remove_watchpoint(self, addr):
        self.remove_watchpoint(addr)
        return True

    def do_watch(self, args):
        if len(args) == 1:
            address = int(args[0], 16)
            self._do_add_watchpoint(address)
            print(f"Watchpoint set at address {address:04x}")
        else:
            print("Invalid number of arguments. Usage: watch <address>")

    def do_unwatch(self, args):
        if len(args) == 1:
            address = int(args[0], 16)
            self._do_remove_watchpoint(address)
            print(f"Watchpoint removed at address {address:04x}")
        else:
            print("Invalid number of arguments. Usage: unwatch <address>")

    # [/watch]

if __name__ == "__main__":
    VirtualMachineBreak.main()
