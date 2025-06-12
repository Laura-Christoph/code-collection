# Exercise 1

## Tests

For vm and assembler there is a test for each operation as well as a count up test which uses the count up file from the Software Design by Example Book as a slighlty more complex test case. Additionally there is an out of memory and instruction not found test case for the vm, which checks that the correct error and error message are returned from the vm in these cases.

## Test Coverage

To view the test coverage for exrecise 1, run the following commands from the exercise 1 directory:

```
$ coverage run -m pytest
$ coverage report -m
```

My tests cover 91% line coverage, where the remaining 9% are lines of code which do not require testing, such as the main function.

# Exercise 3

## Exercise 3.3 Reverse Array in Place

My implementation builds upon the code provided in the Software Design by Example Book. Initially, it creates an array of length 10 and populates it with numbers 1 to 10. Notably, the hexadecimal representation of 10, denoted as 'a', is utilized in this process.

The subsequent segment of the code focuses on reversing the array in place. This is achieved through the utilization of pointers, specifically R0 and R1. R0 acts as a pointer to the beginning of the array, while R1 serves as a pointer to the end of the array.

The reversal process involves using R2 and R3 to temporarily store the values at the positions indicated by R0 and R1. These registers are then employed to swap the values in the array. Following this, R0 is incremented by one, and R1 is decremented by one.

A crucial check is implemented to ensure that the pointers are not pointing to the same point in the array and have not crossed each other, i.e., R0 > R1. If this condition is met, indicating that the array has been successfully reversed, the code proceeds to the conclusion where it halts.

In summary, the implementation efficiently creates and initializes an array, then employs a well-structured and pointer-based approach to reverse the array in place, ensuring a reliable and optimal execution of the algorithm.

# Virtual Machine Debugger

This project implements a virtual machine (VM) and a debugger for running and debugging programs written in a custom assembly language. The VM is extensible and supports various debugging features.


### Show Memory Range

The debugger has been modified to show the value at a single memory address or all memory between two addresses when using the "memory" command.

Example:
#### Show value at a specific address
memory 0x0010

#### Show memory in the range [start_address, end_address]
memory 0x0010 0x0020

### Breakpoint Addresses
The debugger now allows users to set or clear breakpoints at a specified address using the "break" or "clear" command.

#### Usage
##### Set breakpoint at a specific address
break 0x0010

##### Clear breakpoint at a specific address
clear 0x0010

### Command Completion
Command completion has been implemented in the debugger, allowing users to use any number of distinct leading characters to trigger commands. For example, "m," "me," "mem," and so on can now be used to execute the corresponding method.

### Watchpoints
Watchpoints have been introduced, enabling users to specify that the debugger should halt the VM when the value at a particular address changes. Watchpoints can be set and cleared using the "watch" and "unwatch" commands.

#### Usage
##### Set watchpoint at a specific address
watch 0x0010

##### Remove watchpoint at a specific address
unwatch 0x0010
