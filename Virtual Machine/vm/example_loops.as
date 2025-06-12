ldc R0 10
ldc R1 0
ldc R3 1
loop1:
    cpy R2 R1
    add R1 R0
    sub R0 R3
    bne R1 @loop1
ldc R0 5
ldc R1 0
loop2:
    cpy R2 R1
    add R1 R0
    sub R0 R3
    bne R0 @loop2
hlt