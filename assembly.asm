.cpu cortex-m3
.data

word:
	.asciz "fuck\n"

start:
	.asciz "start\n"

calculations:
	.asciz "calculations\n"

true:
	.asciz "true\n"

mid_point:
	.asciz "mid_point\n"

result:
	.asciz "result\n"

.text
.align 2
.global main

main:
	BL wait
	PUSH {LR}
	BL test_end
test_prologue:
	PUSH {LR}
	@ Reserve storage in stack
	SUB SP, SP, #64
	@ Store relevant data in stack
	STR R0, [SP, #12]

	@ If numer < 2
	LDR R0, [SP, #12]
	MOV R1, #2
	CMP R0, R1
	BLO if_true
	B if_false
if_true:
	@ Return numer; R0
	LDR R0, [SP, #12]
	ADD SP, SP, #64
	POP {PC} 
if_false:
	@ jeden = numer - 1
	LDR R0, [SP, #12]
	SUB R0, R0, #1
	STR R0, [SP, #16]
	@ drugi = numer - 2
	LDR R0, [SP, #12]
	SUB R0, R0, #2
	STR R0, [SP, #20]

	@ Load jeden into R0, run function, and store result
	LDR R0, [SP, #16]
	BL test_prologue
	STR R0, [SP, #24]
	@ Load drugi into R0, run function, and store result
	LDR R0, [SP, #20]
	BL test_prologue
	STR R0, [SP, #28]

	@ Combine the results to 1 new number and return it
	LDR R1, [SP, #24]
	LDR R2, [SP, #28]
	ADD R0, R1, R2
	STR R0, [SP, #32]
	LDR R0, [SP, #32]
	ADD SP, SP, #64
	POP {PC}
test_end:
	MOV R0, #12
	BL test_prologue
	BL print_int
	LDR R0, =word
	BL print_asciz
	POP {PC}