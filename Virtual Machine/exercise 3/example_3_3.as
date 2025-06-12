# - R0: loop index.
# - R1: loop limit.
# - R2: array index.
# - R3: temporary.
# - First the program creates and fills an array
ldc R0 0
ldc R1 10
ldc R2 @array
loop:
ldc R3 1
add R0 R3
str R0 R2
sub R0 R3
ldc R3 1
add R0 R3
add R2 R3
cpy R3 R1
sub R3 R0
bne R3 @loop
# - From here we now reverse the array
# - R0 is pointer from start of array
ldc R0 @array
# - R1 is pointer from end of array
ldc R1 @array
# - R2 here is length of array
ldc R2 10
add R1 R2
ldc R3 1
sub R1 R3
cpy R2 R1
sub R2 R0
# - if pointers are pointing to same index, go to end of program
beq R2 @end
mainLoop:
ldr R2 R0
ldr R3 R1
str R2 R1
str R3 R0
ldc R3 1
add R0 R3
sub R1 R3
cpy R2 R1
sub R2 R0
beq R2 @end
ldc R3 1
add R2 R3
# - here we check if the pointers have crossed passed each other in case the array is of even length in which
# - case the pointers wont point to the same index, but instead will pas each other
bne R2 @mainLoop
end:
hlt
.data
array: 10