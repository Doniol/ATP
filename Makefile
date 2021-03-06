# Makefile for .asm on the due
# I am required to first run: "sudo stty -F /dev/ttyACM0 speed 1200 cs8 -cstopb -parenb" before attempting to upload new code to my Arduino Due
# This may not be the case for you

SOURCES:= funcs.cpp
HEADERS:= 
SEARCH:= 
TARGET:= arduino_due
SERIAL_PORT        ?= /dev/ttyACM0
RELATIVE          ?= .
TI-SOFTWARE := ..
HWLIB             ?= $(TI-SOFTWARE)/hwlib

include $(HWLIB)/makefile.inc
