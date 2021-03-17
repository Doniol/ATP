.cpu cortex-m0+
.arch armv7a
.text
.align 1
.global convert

convert:
    MOV R2, #'A'
    SUB R1, R0, R2
    BLT end
    MOV R2, #'Z'
    SUB R1, R0, R2
    BGT other
    ADD R0, R0, #'a' - 'A'
    B end
other:
    MOV R2, #'a'
    SUB R1, R0, R2
    BLT end
    MOV R2, #'z'
    SUB R1, R0, R2
    BGT end
    SUB R0, R0, #'a' - 'A'
end:
    MOV PC, LR
