#include "hwlib.hpp"

extern "C" void print_asciz(const char * c){
   hwlib::wait_ms( 1'000 );
   hwlib::cout 
      << c << hwlib::flush;
}
// // Using the print
// .cpu cortex-m0
// .data
// string:
//     .asciz "Comrades!!"

// .text
// .align 1
// .global main

// main:
//     PUSH {R4, LR}
//     MOV R4, R0
//     LDR R0, =string
//     BL print_asciz
//     POP {R4, PC}