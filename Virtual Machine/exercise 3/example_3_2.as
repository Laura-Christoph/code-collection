# to assemble when in vm folder: python assembler.py '../exercise 3/example_3_2.as' '../exercise 3/output_3_2.mx'
# to vm when in vm folder: python vm.py '../exercise 3/output_3_2.mx' -
#
# showcases swp
ldc R0 0
ldc R1 3
prr R0
prr R1
swp R0 R1
prr R0
prr R1
hlt