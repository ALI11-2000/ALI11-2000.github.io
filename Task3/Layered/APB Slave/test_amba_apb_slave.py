
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
import numpy as np


#Class containing APB driver and monitors 
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
        self.monitor = BusMonitor.__init__(self, entity, name, clock)
        # setting clock value
        self.clock = clock
        # setting default values of input
        self.bus.psel.setimmediatevalue(0)
        self.bus.penable.setimmediatevalue(0)
        self.bus.pwrite.setimmediatevalue(0)
        self.bus.paddr.setimmediatevalue(0)
        self.bus.pwdata.setimmediatevalue(0)

        self.expected_memory = np.zeros(64)
        print("array is",self.expected_memory)
        self.output = []
        self.expected_output = []
        #scoreboard for comparision of actual and expected output 
        self.scoreboard = Scoreboard(entity)
    
    #function describing the reset sequence 
    @cocotb.coroutine
    async def resetseq(self):
        self.bus.preset <= 1
        await RisingEdge(self.clock)
        self.bus.preset <= 1
        await RisingEdge(self.clock)
        self.bus.preset <= 0
    
    #Write function write values from slave 
    @cocotb.coroutine
    async def write(self, addr, data):
        self.bus.psel <= 1
        await RisingEdge(self.clock)
        self.bus.penable <= 1
        self.bus.pwrite <= 1
        self.bus.paddr <= addr
        self.bus.pwdata <= data
        while(self.bus.pready != BinaryValue(1)): await RisingEdge(self.clock)
        await RisingEdge(self.clock)
        self.bus.penable <= 0
        await RisingEdge(self.clock)
    
    #Read function takes values from slave 
    @cocotb.coroutine
    async def read(self, addr):
        self.bus.psel <= 1
        await RisingEdge(self.clock)
        self.bus.penable <= 1
        self.bus.pwrite <= 0
        self.bus.paddr <= addr
        while(self.bus.pready != BinaryValue(1)): await RisingEdge(self.clock)
        await RisingEdge(self.clock)
        self.bus.penable <= 0
        await RisingEdge(self.clock)
    
    #Monitor recieve is the recieving function that recieve values 
    @cocotb.coroutine
    async def _monitor_recv(self):
        while (True):
            await RisingEdge(self.clock)
            transaction = dict(self.bus.capture())
            #print("in monitor we have",transaction)
            if int(self.bus.pready) == 1 :
                self._recv(transaction)
                print("Input sampled is",transaction)
                self.apb_slave_model(transaction)
    
    def apb_slave_model(self,transaction):
        if(int(transaction['pwrite'])==1):
            self.expected_memory[int(transaction['paddr'])-1] = int(transaction['pwdata'])
    

@cocotb.test()
async def amba_apba_slave_basic_test(dut):
    """Basic Test"""
    #clock generator function called with 10 ns frequency
    clock = Clock(dut.pclk,10,units="ns")
    #clock started in parallel 
    cocotb.fork(clock.start())
    #object instantiation of slave test bench class
    tb = amba_apba_slave_tb(dut,name="",clock=dut.pclk)
    await tb.resetseq()
    await tb.write(5,10)
    await tb.read(5)
    #Reads the value from the given value
    await tb.read(1)
    #Printing the expected value from the memory
    print("expected memory is",tb.expected_memory)
