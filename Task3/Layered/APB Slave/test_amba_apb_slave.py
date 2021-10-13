
import logging
from typing import Awaitable, Literal
import cocotb
from cocotb import clock
from cocotb.decorators import coroutine
from cocotb.triggers import Event, FallingEdge, RisingEdge, Timer, Trigger
import random
from cocotb.result import TestFailure
import cocotb_bus
from cocotb_bus.monitors import BusMonitor
from cocotb_bus.drivers import BusDriver
from cocotb_bus.scoreboard import Scoreboard
from cocotb.clock import Clock
from cocotb.binary import BinaryValue
import logging
import numpy as np

class amba_apb_slave_tb (BusMonitor,BusDriver):

    # monitor to be used at input and output of the DUT
    _signals = [
        "pclk","preset","psel","penable","pwrite",\
        "paddr","pwdata","pready","prdata"
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
        self.bus.psel.setimmediatevalue(0)
        self.bus.penable.setimmediatevalue(0)
        self.bus.pwrite.setimmediatevalue(0)
        self.bus.paddr.setimmediatevalue(0)
        self.bus.pwdata.setimmediatevalue(0)

        self.expected_memory = np.zeros(64)
        #print("array is",self.expected_memory)
        self.output = []
        self.expected_output = []
        self.expected_transaction = []
        #scoreboard for comparision of actual and expected output 
        self.scoreboard = Scoreboard(entity,0,False)
        self.scoreboard._imm = False
        #self.scoreboard.add_interface(self.monitor, self.expected_transaction)
    
    #function describing the reset sequence 
    @cocotb.coroutine
    async def resetseq(self):
        self.bus.preset <= 1
        await RisingEdge(self.clock)
        self.bus.preset <= 1
        await RisingEdge(self.clock)
        self.bus.preset <= 0
    
    #Write function writes values to slave 
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
                #if(self.last_transaction != transaction):
                    self._recv(transaction)
                    #print("Input sampled is",transaction)
                    if((transaction['pwrite']) == BinaryValue(0)):
                        self.output.append((transaction['prdata']))
                    self.apb_slave_model(transaction)
                    #print(self.output,self.expected_output)
                    if(self.output != self.expected_output):
                        self.log.error("Test failed for transaction %s",transaction)
                    #self.scoreboard.compare(self.output,self.expected_output,log=logging.log(level=0,msg="error raised"),strict_type=True)
            self.last_transaction = transaction
    
    def apb_slave_model(self,transaction):
        if(int(transaction['pwrite'])==1):
            self.expected_memory[int(transaction['paddr'])-1] = int(transaction['pwdata'])
        else:
            self.expected_output.append(self.expected_memory[int(transaction['paddr'])-1])
    
@cocotb.test()
async def amba_apba_slave_basic_test(dut):
    """Basic Test"""
    #clock generator function called with 10 ns frequency
    clock = Clock(dut.pclk,10,units="ns")
    #clock started in parallel 
    cocotb.fork(clock.start())
    #object instantiation of slave test bench class
    tb = amba_apb_slave_tb(dut,"",clock=dut.pclk)
    await tb.resetseq()
    await tb.write(5,10)
    await tb.write(11,20)
    await tb.write(13,30)
    await tb.read(5)
    #Reads the value from the given value
    await tb.read(1)
    await tb.read(11)
    #print("expected memory is",tb.expected_memory)
