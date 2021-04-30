.cpu cortex-m0
.text
.align 2
.global main

word:
    .asciz "word"

other_word:
    .asciz "other_word"

main:
    PUSH {R4, LR}
@ Print standard word
    LDR R0, =word
    BL print_asciz

@ Change contents of word:
@ Load address of word into register
    LDR R0, =word
@ Load new word into another register
    LDR R6, =other_word
    LDR R5, [R6]
@ Store new word in registered address
    STR R5, [R0]

@ Print changed word
    LDR R0, =word
    BL print_asciz
end:
    POP {R4, PC}
