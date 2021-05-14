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
	.int 0

resultat:
	.int 0

.text
.align 2
.global main

main:
	PUSH {R4, LR}
	POP {R4, PC}