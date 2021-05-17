.cpu cortex-m0
.data

numer:
	.int 0

jeden:
	.int 0

drugi:
	.int 0

pierwsza:
	.int 0

druga:
	.int 0

totalna:
	.int 0

liczba:
	.int 12

resultat:
	.int 0

.text
.align 2
.global main

main:
	PUSH {LR}
	BL _fiba_end
_fiba:
	PUSH {LR}
	PUSH {R8}
	LDR R8, =numer
	STR R0, [R8]
	POP {R8}
	LDR R0, =numer
	LDR R0, [R0]
	MOV R0, #2
	CMP R0, R1
	BLO _45_if_true
	BL _45_if_false
_45_if_true:
	LDR R0, =numer
	LDR R0, [R0]
	POP {PC}
_45_if_false:
	LDR R0, =jeden
	MOV R2, #-1
	LDR R3, =numer
	LDR R3, [R3]
	ADD R1, R2, R3
	STR R1, [R0]
	LDR R0, =drugi
	MOV R2, #-2
	LDR R3, =numer
	LDR R3, [R3]
	ADD R1, R2, R3
	STR R1, [R0]
	LDR R0, =jeden
	LDR R0, [R0]
	BL fiba
	LDR R1, =pierwsza
	STR R0, [R1]
	LDR R0, =drugi
	LDR R0, [R0]
	BL fiba
	LDR R1, =druga
	STR R0, [R1]
	LDR R0, =totalna
	LDR R2, =pierwsza
	LDR R2, [R2]
	LDR R3, =druga
	LDR R3, [R3]
	ADD R1, R2, R3
	STR R1, [R0]
	LDR R0, =totalna
	LDR R0, [R0]
	POP {PC}
	POP {PC}
_fiba_end:
	LDR R0, =liczba
	LDR R0, [R0]
	BL fiba
	LDR R1, =resultat
	STR R0, [R1]
	PUSH {R0-R6}
	LDR R0, =resultat
	BL print_asciz
	POP {R0-R6}
	POP {PC}