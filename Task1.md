# Task 1: ALU
For the first task, which was to simulate a combinational circuit we used an ALU with following operations.
|Selection Value|Operation  |
|--|--|
| 0 | A + B |
| 1 | A - B |
| 2 | A > B |
| 3 | A & B |
| 4 | A \| B |
| 5 | A ^ B|
|6|A|
|7|B|
For that purpose we created the following verilog design.

    `timescale 1ns/1ns
    
    module alu #(
        parameter integer width = 5
    ) (
        output reg [width:0] X,
        input [width:0] A,B,input [3:0] sel
    );
        always_comb begin 
            case (sel)
                4'd0: X = A + B;
                4'd1: X = A - B;
                4'd2: X = A > B;
                4'd3: X = A & B;
                4'd4: X = A | B;
                4'd5: X = A ^ B;
                4'd6: X = A;
                4'd7: X = B;
                default: X = A;
            endcase
        end
        
    endmodule
We created the following model for the ALU in python.

    def alu_model(a:int,b:int,sel:int):
        X=[a+b,a-b,0,(a) & (b), (a) | (b),(a) ^ (b),a,b]
        if(sel==2):
            if(int(a)>int(b)):
                return 1
            else:
                return 0
        return X[sel]

For the above design, we have the following cocotb test bench.

    import cocotb
    from cocotb.triggers import Timer
    from alu_model import alu_model
    import random
    import logging
    
    @cocotb.test()
    async def alu_test(dut):
        x=['+','-','>','&','|','^','A','B']
        dut.A.value = 10
        dut.B.value = 5
        for i in range(0,len(x)):
            dut.sel.value = i
            await Timer(2,units='ns')
            output1=alu_model(dut.A.value,dut.B.value,i)
            assert dut.X.value == output1, "Randomised test failed with: {A}  {y}  {B} = {X} for {a}".format(A=dut.A.value, B=dut.B.value, X=dut.X.value,y=x[i],a=output1)
Following Makefile has been used.

    TOPLEVEL_LANG ?= verilog
    PWD = $(shell pwd)
    export PYTHONPATH := $(PWD):$(PYTHONPATH)
    VERILOG_SOURCES = alu.sv
    TOPLEVEL := alu
    MODULE := test_alu
    include $(shell cocotb-config --makefiles)/Makefile.sim
    
    
    
    .PHONY: clean
    clean::
            rm -rf *.vcd *.xml __pycache__ sim_build

> Written with [StackEdit](https://stackedit.io/).
