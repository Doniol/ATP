.cpu cortex-m3
.text
.align 2
.global main

main:
	BL wait
	PUSH {LR}
	SUB SP, SP, #8
@Define function
	B _fiba_end
_fiba:
	PUSH {LR}
	SUB SP, SP, #24
	STR R0, [SP, #0]
@If-statement
	LDR R0, [SP, #0]
	MOV R1, #2
	CMP R0, R1
	BLO _45_if_true
	B _45_if_end
_45_if_true:
@Return
	LDR R0, [SP, #0]
	ADD SP, SP, #24
	POP {PC}
_45_if_end:
MOV R0, #0
	STR R0, [SP, #4]
MOV R0, #0
	STR R0, [SP, #8]
@Change Variable
	MOV R3, #1
	LDR R2, [SP, #0]
	SUB R1, R2, R3
	STR R1, [SP, #4]
@Change Variable
	MOV R3, #2
	LDR R2, [SP, #0]
	SUB R1, R2, R3
	STR R1, [SP, #8]
MOV R0, #0
	STR R0, [SP, #12]
MOV R0, #0
	STR R0, [SP, #16]
@Execute Function
	LDR R0, [SP, #4]
	BL _fiba
	STR R0, [SP, #12]
@Execute Function
	LDR R0, [SP, #8]
	BL _fiba
	STR R0, [SP, #16]
MOV R0, #0
	STR R0, [SP, #20]
@Change Variable
	LDR R2, [SP, #12]
	LDR R3, [SP, #16]
	ADD R1, R2, R3
	STR R1, [SP, #20]
@Return
	LDR R0, [SP, #20]
	ADD SP, SP, #24
	POP {PC}
	ADD SP, SP, #24
	POP {PC}
_fiba_end:
MOV R0, #12
	STR R0, [SP, #0]
MOV R0, #0
	STR R0, [SP, #4]
@Execute Function
	LDR R0, [SP, #0]
	BL _fiba
	STR R0, [SP, #4]
@Print
	LDR R0, [SP, #4]
	BL print_asciz
	LDR R0, [SP, #4]
	BL print_int
	SUB SP, SP, #8
	POP {PC}
