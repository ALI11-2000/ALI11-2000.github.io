TOPLEVEL_LANG ?= verilog
PWD = $(shell pwd)
export PYTHONPATH := $(PWD):$(PYTHONPATH)
VERILOG_SOURCES = top.v
TOPLEVEL := top
MODULE := test_alu
include $(shell cocotb-config --makefiles)/Makefile.sim



.PHONY: clean
clean::
	rm -rf *.vcd *.xml __pycache__ sim_build