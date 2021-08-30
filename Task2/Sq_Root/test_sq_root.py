import cocotb
from cocotb import clock
import cocotb.triggers
from cocotb.clock import Clock
import random
from sq_root_model import sq_root_model
import logging

@cocotb.test()
async def sq_root_test(dut):
    clock = Clock(dut.clk,10,units="ns")
    cocotb.fork(clock.start())
    for i in range(2):
        await cocotb.triggers.RisingEdge(dut.clk)
        dut.reset=1
    dut.reset=0

    for i in range(1000):
        dut.ready=1
        input_value = random.randint(1,100)
        dut.num = input_value
        await cocotb.triggers.RisingEdge(dut.clk)
        dut.ready=0
        await cocotb.triggers.FallingEdge(dut.done)
        dut._log.info("Square root of %d is %d by python we get %d",int(dut.num),int(dut.res),sq_root_model(input_value))
        assert dut.res == sq_root_model(input_value),"Assertion error at num = {A} we get {B} but model value is {C}".format(A=dut.num,B=dut.res,C=sq_root_model(input_value))