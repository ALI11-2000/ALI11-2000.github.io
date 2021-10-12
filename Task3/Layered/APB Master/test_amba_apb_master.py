
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

class amba_apb_master_tb (BusMonitor,BusDriver):

    # monitor to be used at input and output of the DUT
    _signals = [
        "pclk","preset","transfer","mpwrite","pready",
        "apb_write_paddr","apb_write_data","apb_read_paddr","prdata",
        "psel","penable","spwrite",
        "paddr","pwdata","apb_read_data_out"
    ]

    def __init__(self,entity,name,clock):
        # driver initialization
        self.driver = BusDriver.__init__(self, entity, name, clock)
        # monitor initialization
        self.monitor = BusMonitor.__init__(self, entity, name, clock,callback=None)
        # setting clock value
        self.clock = clock
        self.last_transaction = {}
        # setting default values of input
        self.bus.pclk.setimmediatevalue(0)
        self.bus.preset.setimmediatevalue(0)
        self.bus.transfer.setimmediatevalue(0)
        self.bus.mpwrite.setimmediatevalue(0)
        self.bus.pready.setimmediatevalue(0)
        self.bus.apb_write_paddr.setimmediatevalue(0)
        self.bus.apb_write_data.setimmediatevalue(0)
        self.bus.apb_read_paddr.setimmediatevalue(0)
        self.bus.prdata.setimmediatevalue(0)
        

        self.expected_memory = np.zeros(64)
        #print("array is",self.expected_memory)
        self.output = []
        self.expected_output = []
        self.expected_transaction = []
        #scoreboard for comparision of actual and expected output 
        self.scoreboard = Scoreboard(entity)
        #self.scoreboard.add_interface(self.monitor, self.expected_transaction)
    
    #function describing the reset sequence 
    @cocotb.coroutine
    async def resetseq(self):
        self.bus.preset <= 1
        await RisingEdge(self.clock)
        self.bus.preset <= 1
        await RisingEdge(self.clock)
        self.bus.preset <= 0
    
    #Write function writes values to master
    @cocotb.coroutine
    async def write(self, addr, data):
        self.bus.transfer <= 1
        self.bus.mpwrite <= 1
        self.bus.pready <= 1
        self.bus.apb_write_paddr <= addr
        self.bus.apb_write_data <= data
        await RisingEdge(self.clock)
        self.bus.pready <= 0
        self.bus.transfer <= 0
    
    #Read function takes values from master
    @cocotb.coroutine
    async def read(self, addr):
        self.bus.transfer <= 1
        self.bus.mpwrite <= 0
        self.bus.pready <= 1
        self.bus.apb_write_paddr <= addr
        await RisingEdge(self.clock)
        self.bus.pready <= 0
        self.bus.transfer <= 0
    
    #Monitor recieve is the recieving function that recieve values 
    @cocotb.coroutine
    async def _monitor_recv(self):
        while (True):
            await RisingEdge(self.clock)
            transaction = dict(self.bus.capture())
            #print("in monitor we have",transaction)
        
            self.last_transaction = transaction
    
    def apb_master_model(self,transaction):
        self.expected_transaction = {'pclk': 1, 'preset': 0, 'psel': 1, 'penable': 1, 'pwrite': 1,\
                                     'paddr': 0, 'pwdata': 0, 'pready': 1, 'prdata': 00000000}
        
        
    

@cocotb.test()
async def amba_apba_master_basic_test(dut):
    """Basic Test"""
    #clock generator function called with 10 ns frequency
    clock = Clock(dut.pclk,10,units="ns")
    #clock started in parallel 
    cocotb.fork(clock.start())
    #object instantiation of master test bench class
    tb = amba_apb_master_tb(dut,"",clock=dut.pclk)
    await tb.resetseq()
    await tb.write(5,10)
    await tb.write(11,20)
    await tb.write(13,30)
    await tb.read(5)
    #Reads the value from the given value
    await tb.read(1)
    await tb.read(11)
    print("expected memory is",tb.expected_memory)
