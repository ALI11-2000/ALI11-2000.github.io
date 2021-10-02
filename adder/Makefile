TOPLEVEL_LANG ?= verilog

PWD=$(shell pwd)
VERILOG_SOURCES = adder.sv

TOPLEVEL := adder
MODULE   := test_adder

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: clean
clean::
	rm -rf __pycache__ *.vcd *.xml