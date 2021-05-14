.cpu cortex-m0
.data

word:
    .asciz "word\n"

second_word:
    .asciz "seco\n"

third_word:
    .asciz "thir\n"

number:
    .int 3

second_number:
    .int 0

.text
.align 2
.global main

main:
    PUSH {LR}
    BL print_R2_end
print_R2:
    PUSH {R0-R2, LR}
    LDR R0, =second_word
    PUSH {R0, R2}
    BL print_asciz
    POP {R0, R2}
    STR R2, [R0]
    LDR R0, =second_word
    BL print_asciz
    POP {R0-R2, PC}
print_R2_end:
    LDR R0, =third_word
    BL print_asciz
    LDR R2, =word
    LDR R2, [R2]
    BL print_R2
	POP {PC}
