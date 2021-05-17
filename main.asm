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
    LDR R1, =word
    MOV R0, "test"
    LDR R0, [R1]
    LDR R0, =word
    BL print_asciz
	POP {PC}
