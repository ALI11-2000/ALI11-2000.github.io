TOPLEVEL_LANG ?= verilog
PWD = $(shell pwd)
export PYTHONPATH := $(PWD):$(PYTHONPATH)
VERILOG_SOURCES = top_amba_apb.sv
TOPLEVEL := top_amba_apb
MODULE := test_top_amba_apb
include $(shell cocotb-config --makefiles)/Makefile.sim



.PHONY: clean
clean::
	rm -rf *.vcd *.xml __pycache__ sim_build