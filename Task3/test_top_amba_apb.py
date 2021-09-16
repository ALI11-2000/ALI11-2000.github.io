from os import write
import cocotb
from cocotb import clock
import cocotb.triggers
from cocotb.clock import Clock
import random
import logging
from cocotb.handle import SimHandleBase
import numpy
from numpy import zeros


async def resetapb(dut):
    dut._log.info("Starting reset Sequence")
    clock = Clock(dut.pclk,10,units="ns")
    cocotb.fork(clock.start())
    dut.preset = 1
    dut.transfer = 0
    dut.mpwrite = 0
    dut.apb_write_paddr = 0
    dut.apb_write_data = 0
    for i in range(3): await cocotb.triggers.RisingEdge(dut.pclk)
    dut.preset = 0

    for i in range(32):
        dut.transfer = 1
        dut.mpwrite = 1
        dut.apb_write_paddr = i
        dut.apb_write_data = 0
        await cocotb.triggers.FallingEdge(dut.pready)
        await cocotb.triggers.RisingEdge(dut.pclk)
    dut.preset = 0
    dut._log.info("Reset sequence completed")

async def basictest(dut):
    expected_val=numpy.zeros(32)
    dut._log.info("Basic Check Test")
    clock = Clock(dut.pclk,10,units='ns')
    cocotb.fork(clock.start())
    for i in range(32):
        dut.transfer = 1
        dut.mpwrite = 1
        dut.apb_write_paddr = random.randint(0,31)
        dut.apb_write_data = random.randint(0,50)
        await cocotb.triggers.FallingEdge(dut.pready)
        await cocotb.triggers.RisingEdge(dut.pclk)
        if(int(dut.mpwrite)==1):
            expected_val[int(dut.apb_write_paddr)] = int(dut.apb_write_data)

    print("Expected array is ",expected_val)

    for i in range(32):
        dut.transfer = 1
        dut.mpwrite = 0
        dut.apb_write_paddr = i
        dut.apb_write_data = random.randint(0,11)
        await cocotb.triggers.FallingEdge(dut.pready)
        await cocotb.triggers.RisingEdge(dut.pclk)
        #print("Expected value is",expected_val[int(dut.apb_write_paddr)],"Actual value is",int(dut.prdata))
        
        assert int(expected_val[int(dut.apb_write_paddr)]) == int(dut.prdata) ,"Assertion error for {A} != {B}".format(A=(expected_val[int(dut.apb_write_paddr)]),B=int(dut.prdata))
    
    dut._log.info("Basic Check Test Complete")
    print("Expected array is ",expected_val)


@cocotb.test()
async def top_amba_apb_test(dut):
    await resetapb(dut)
    await basictest(dut)

