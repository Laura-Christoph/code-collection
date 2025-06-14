import sys
import readline  

from architecture import VMState
from vm_step import VirtualMachineStep


class VirtualMachineExtend(VirtualMachineStep):
    # [init]
    def __init__(self, reader=input, writer=sys.stdout):
        super().__init__(reader, writer)
        self.handlers = {
            "d": self._do_disassemble,
            "dis": self._do_disassemble,
            "i": self._do_ip,
            "ip": self._do_ip,
            "m": self._do_memory,
            "memory": self._do_memory,
            "q": self._do_quit,
            "quit": self._do_quit,
            "r": self._do_run,
            "run": self._do_run,
            "s": self._do_step,
            "step": self._do_step,
        }
    # [/init]

    # [interact]
    def interact(self, addr):
        prompt = "".join(sorted({key[0] for key in self.handlers}))
        interacting = True
        while interacting:
            try:
                command = self.read(f"{addr:06x} [{prompt}]> ")
                if not command:
                    continue
                elif command not in self.handlers:
                    self.write(f"Unknown command {command}")
                else:
                    interacting = self.handlers[command](self.ip)
            except EOFError:
                self.state = VMState.FINISHED
                interacting = False
    # [/interact]

    def _do_disassemble(self, addr):
        self.write(self.disassemble(addr, self.ram[addr]))
        return True

    def _do_ip(self, addr):
        self.write(f"{self.ip:06x}")
        return True

    # [memory]
    def _do_memory(self, addr):
        """
        Show memory at a specific address or in a range of addresses.
        
        addr: The address or range of addresses to show.
        Output: The memory at the specified address(es).
        """
        args = addr.split()
        if len(args) == 1:
            # Show the value at a specific address
            address_to_show = int(args[0], 16)
            value = self.read_memory(address_to_show)
            if value is not None:
                self.write(f"Memory at address {address_to_show:06x}: {value:06x}")
        elif len(args) == 2:
            # Show memory in the range [start_address, end_address]
            start_address = int(args[0], 16)
            end_address = int(args[1], 16)
            for address in range(start_address, end_address + 1):
                value = self.read_memory(address)
                if value is not None:
                    self.write(f"Memory at address {address:06x}: {value:06x}")
        else:
            self.show()
        return True
    # [/memory]


    def _do_quit(self, addr):
        self.state = VMState.FINISHED
        return False

    def _do_run(self, addr):
        self.state = VMState.RUNNING
        return False

    # [step]
    def _do_step(self, addr):
        self.state = VMState.STEPPING
        return False
    # [/step]

    # [completion]
    def handle_command_completion(self, text, state):
        commands = ['d', 'dis', 'i', 'ip', 'm', 'memory', 'q', 'quit', 'r', 'run', 's', 'step']
        options = [cmd for cmd in commands if cmd.startswith(text)]
        return options[state] if state < len(options) else None
    # [/completion]


if __name__ == "__main__":
        # Set up command completion
        readline.set_completer(VirtualMachineExtend().handle_command_completion)
        readline.parse_and_bind("tab: complete")

        # Start your debugger
        VirtualMachineExtend.main()
