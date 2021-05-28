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
	SUB SP, SP, #24
	@ Store relevant data in stack
	STR R0, [SP]

	@ If numer < 2
	LDR R0, [SP]
	MOV R1, #2
	CMP R0, R1
	BLO if_true
	B if_false
if_true:
	@ Return numer; R0
	LDR R0, [SP]
	ADD SP, SP, #24
	POP {PC} 
if_false:
	@ jeden = numer - 1
	LDR R0, [SP]
	SUB R0, R0, #1
	STR R0, [SP, #4]
	@ drugi = numer - 2
	LDR R0, [SP]
	SUB R0, R0, #2
	STR R0, [SP, #8]

	@ Load jeden into R0, run function, and store result
	LDR R0, [SP, #4]
	BL test_prologue
	STR R0, [SP, #12]
	@ Load drugi into R0, run function, and store result
	LDR R0, [SP, #8]
	BL test_prologue
	STR R0, [SP, #16]

	@ Combine the results to 1 new number and return it
	LDR R1, [SP, #12]
	LDR R2, [SP, #16]
	ADD R0, R1, R2
	STR R0, [SP, #20]
	LDR R0, [SP, #20]
	ADD SP, SP, #24
	POP {PC}
test_end:
	MOV R0, #12
	BL test_prologue
	BL print_int
	POP {PC}