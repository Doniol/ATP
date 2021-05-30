string:
	.asciz ""

word:
	.asciz "test"

.cpu cortex-m3
.text
.align 2
.global main

main:
	BL wait
	PUSH {LR}
	SUB SP, SP, #12
@Define function
	B _func_name_end
_func_name:
	PUSH {LR}
	SUB SP, SP, #8
	STR R0, [SP, #0]
	STR R1, [SP, #4]
@While-loop
_36_while:
	LDR R0, [SP, #0]
	MOV R1, #0
	CMP R0, R1
	BHI _36_while_loop
	B _36_while_end
_36_while_loop:
@Print
	LDR R0, [SP, #4]
	BL print_asciz
@Change Variable
	LDR R2, [SP, #0]
	MOV R3, #1
	SUB R1, R2, R3
	STR R1, [SP, #0]
	B _36_while
_36_while_end:
@Return
	LDR R0, [SP, #0]
	ADD SP, SP, #8
	POP {PC}
	ADD SP, SP, #8
	POP {PC}
_func_name_end:
	MOV R0, #3
	STR R0, [SP, #0]
	LDR R0, =word
	STR R0, [SP, #4]
	MOV R0, #0
	STR R0, [SP, #8]
@Execute Function
	LDR R0, [SP, #0]
	LDR R1, [SP, #4]
	BL _func_name
	STR R0, [SP, #8]
@Print
	LDR R0, [SP, #8]
	BL print_int
	SUB SP, SP, #12
	POP {PC}
