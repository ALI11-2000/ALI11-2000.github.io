#importing required libraries
import cocotb
from cocotb.triggers import Timer
from alu_model import alu_model #importing ALU model
import random
import logging

#initiating cocotb test
@cocotb.test()
async def alu_test(dut):
    x=['+','-','>','&','|','^','A','B']
    for i in range(0,1000):
        #randomly populating A and B
        A = random.randint(0,10)
        B = random.randint(0,10)
        sel = random.randint(0,7)
        
        dut.A.value = A
        dut.B.value = B
        dut.sel.value = sel
        
        #awaiting 2ns
        await Timer(2,units='ns')
        output1=alu_model(A,B,sel)
        
        #showing the output log info
        dut._log.info( "Randomised test with: %d  {y}  %d = %d for model \
        value {a}".format(y=x[sel],a=output1),dut.A.value,dut.B.value,dut.X.value)
        
        #asserting error if the test fails
        assert dut.X.value == output1, "Randomised test failed with: {A} \
        {y}  {B} = {X} for {a}".format(A=dut.A.value, B=dut.B.value,     \
        X=dut.X.value,y=x[sel],a=output1)
