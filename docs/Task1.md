# Task 1: ALU
For the first task, which was to simulate a combinational circuit we used an ALU with following operations.


|Selection Value|Operation  |
|--|--|
| 0 | A + B |
| 1 | A - B , B - A |
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
                4'd1: begin 
                    if ( A > B)
                        X = A - B;
                    else
                        X = B - A;
                end
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
        X=[a+b,abs(int(a-b)),a+b,(a) & (b), (a) | (b),(a) ^ (b),a,b]
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
        for i in range(0,1000):
            A = random.randint(0,10)
            B = random.randint(0,10)
            sel = random.randint(0,7)
            dut.A.value = A
            dut.B.value = B
            dut.sel.value = sel
            await Timer(2,units='ns')
            output1=alu_model(A,B,sel)
            dut._log.info( "Randomised test with: %d  {y}  %d = %d for model value {a}".format(y=x[sel],a=output1),dut.A.value,dut.B.value,dut.X.value)
            assert dut.X.value == output1, "Randomised test failed with: {A}  {y}  {B} = {X} for {a}".format(A=dut.A.value, B=dut.B.value, X=dut.X.value,y=x[sel],a=output1)
        
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
        

[Prev](README.md)|[Next](Task2.md)
