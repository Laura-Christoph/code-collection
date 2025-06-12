# to assemble when in vm folder: python assembler.py '../exercise 3/example_3_1.as' '../exercise 3/output_3_1.mx'
# to vm when in vm folder: python vm.py '../exercise 3/output_3_1.mx' -
#
# Count up to 3.
# - R0: loop index.
# - R1: loop limit.
ldc R0 0
ldc R1 3
loop:
prr R0
inc R0
prr R0
inc R0
prr R0
dec R0
prr R0
cpy R2 R1
sub R2 R0
bne R2 @loop
hlt
