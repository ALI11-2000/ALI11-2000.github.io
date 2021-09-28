#importing the required libraries
import cocotb
from cocotb import clock
import cocotb.triggers
from cocotb.clock import Clock
import random
#importing the square root model
from sq_root_model import sq_root_model
import logging

#initiating the cocotb test
@cocotb.test()
async def sq_root_test(dut):
    #defining the clock
    clock = Clock(dut.clk,10,units="ns")
    cocotb.fork(clock.start())
    for i in range(2):
        await cocotb.triggers.RisingEdge(dut.clk)
        dut.reset=1
    dut.reset=0

    for i in range(1000):
        dut.ready=1
        #after the ready is 1, we randomly  populate the input value
        input_value = random.randint(1,100)
        dut.num = input_value #giving the input value to the design under test
        await cocotb.triggers.RisingEdge(dut.clk) #awaiting a rising edge
        dut.ready=0 #resetting ready back to 0
        await cocotb.triggers.FallingEdge(dut.done)
        #showing the output of the program
        dut._log.info("Square root of %d is %d by python we get %d",int(dut.num),int(dut.res),sq_root_model(input_value))
        #assert an error incase the test fails
        assert dut.res == sq_root_model(input_value),"Assertion error at num = {A} we get {B} but model value is {C}".format(A=dut.num,B=dut.res,C=sq_root_model(input_value))