# sudo stty -F /dev/ttyACM0 speed 1200 cs8 -cstopb -parenb

SOURCES:= funcs.cpp
HEADERS:= 
SEARCH:= 
TARGET:= arduino_due
SERIAL_PORT        ?= /dev/ttyACM0
RELATIVE          ?= .
TI-SOFTWARE := ..
HWLIB             ?= $(TI-SOFTWARE)/hwlib

include $(HWLIB)/makefile.inc