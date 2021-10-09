import logging
from typing import Awaitable
import cocotb
from cocotb import clock
from cocotb.decorators import coroutine
from cocotb.triggers import Event, FallingEdge, RisingEdge, Timer, Trigger
import random
from cocotb.result import TestFailure
from cocotb_bus.monitors import BusMonitor
from cocotb_bus.drivers import BusDriver
from cocotb_bus.scoreboard import Scoreboard
from cocotb.clock import Clock
from cocotb.binary import BinaryValue
import logging



class amba_apba_slave_tb(BusDriver,BusMonitor):
    # APB slave signals
    _signals = [
        "pclk","preset","psel","penable","pwrite",\
        "paddr","pwdata","pready","prdata"
    ]

    def __init__(self,entity,name,clock):
        # driver initialization
        self.driver = BusDriver.__init__(self, entity, name, clock)
        # monitor initialization
        #self.monitor = BusMonitor.__init__(self, entity, name, clock)
        # setting clock value
        self.clock = clock
        # setting default values of input
        self.bus.psel.setimmediatevalue(0)
        self.bus.penable.setimmediatevalue(0)
        self.bus.pwrite.setimmediatevalue(0)
        self.bus.paddr.setimmediatevalue(0)
        self.bus.pwdata.setimmediatevalue(0)

        self.output = []
        self.expected_output = []
        self.scoreboard = Scoreboard(entity)
    
    @cocotb.coroutine
    async def resetseq(self):
        self.bus.preset <= 1
        await RisingEdge(self.clock)
        self.bus.preset <= 1
        await RisingEdge(self.clock)
        self.bus.preset <= 0
    
    @cocotb.coroutine
    async def write(self, addr, data):
        self.bus.psel <= 1
        self.bus.penable <= 1
        self.bus.pwrite <= 1
        self.bus.paddr <= addr
        self.bus.pwdata <= data
        while(self.bus.pready != BinaryValue(1)): await RisingEdge(self.clock)
        await RisingEdge(self.clock)
        self.bus.penable <= 0
        await RisingEdge(self.clock)
    
    @cocotb.coroutine
    async def read(self, addr):
        self.bus.psel <= 1
        self.bus.penable <= 1
        self.bus.pwrite <= 0
        self.bus.paddr <= addr
        while(self.bus.pready != BinaryValue(1)): await RisingEdge(self.clock)
        await RisingEdge(self.clock)
        self.bus.penable <= 0
        await RisingEdge(self.clock)
    

@cocotb.test()
async def amba_apba_slave_basic_test(dut):
    """Basic Test"""
    clock = Clock(dut.pclk,10,units="ns")
    cocotb.fork(clock.start())
    tb = amba_apba_slave_tb(dut,name="",clock=dut.pclk)
    await tb.resetseq()
    await tb.write(5,10)
    await tb.read(5)
    await tb.read(1)
