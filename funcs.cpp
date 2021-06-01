#include "hwlib.hpp"

extern "C" void wait(){
   hwlib::wait_ms(1'000);
}

extern "C" void print_asciz(const char * c){
   hwlib::cout << c << "\n" << hwlib::flush;
}

extern "C" void print_int(int i){
   hwlib::cout << i << "\n" << hwlib::flush;
}
