TOPLEVEL_LANG ?= verilog
PWD = $(shell pwd)
export PYTHONPATH := $(PWD):$(PYTHONPATH)
VERILOG_SOURCES = amba_apb_master.sv
TOPLEVEL := amba_apb_master
MODULE := test_amba_apb_master
include $(shell cocotb-config --makefiles)/Makefile.sim



.PHONY: clean
clean::
	rm -rf *.vcd *.xml __pycache__ sim_build