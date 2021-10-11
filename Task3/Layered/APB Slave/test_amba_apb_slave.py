
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

class Monitor1 (BusMonitor):

    # monitor to be used at input and output of the DUT
    _signals = [
        "pclk","preset","psel","penable","pwrite",\
        "paddr","pwdata","pready","prdata"
    ]

    def __init__(self, dut, name, clock, reset=None, reset_n=None, callback=None, event=None, bus_separator=None):
        # Bus monitor initalized
        BusMonitor.__init__(self, dut, name=name, clock=clock, reset=reset, reset_n=reset_n, callback=callback, event=event, bus_separator=bus_separator)
        # check for duplicate sampling
        self.last_Transaction = None

    #Monitor recieve is the recieving function that recieve values 
    @cocotb.coroutine
    async def _monitor_recv(self):
        while (True):
            await RisingEdge(self.clock)
            transaction = dict(self.bus.capture())
            #print("in monitor we have",transaction)
            if int(self.bus.pready) == 1 :    
                if(self.last_transaction != transaction):
                    self._recv(transaction)
                    #print("Input sampled is",transaction)
                    if(int(transaction['pwrite']) == 0):
                        self.output.append(int(transaction['prdata']))
                    #self.apb_slave_model(transaction)
                    #print(self.output,self.expected_output)
                    self.scoreboard.add_interface(self.monitor,self.expected_transaction)
            self.last_transaction = transaction

class Driver1 (BusDriver):
    _signals = [
        "pclk","preset","psel","penable","pwrite",\
        "paddr","pwdata"
    ]

    def __init__(self, dut, name, clock):
        BusDriver.__init__(self, dut, name,clock)
        # setting default values of input
        self.bus.psel.setimmediatevalue(0)
        self.bus.penable.setimmediatevalue(0)
        self.bus.pwrite.setimmediatevalue(0)
        self.bus.paddr.setimmediatevalue(0)
        self.bus.pwdata.setimmediatevalue(0)
 

#Class containing APB driver and monitors 
class amba_apba_slave_tb(object):
    # APB slave signals
    

    def __init__(self,dut,name,clock):
        # driver initialization
        self.dut = dut
        self.driver = Driver1(self.dut, name, clock)
    
        
        self.transaction = {'pclk': 1, 'preset': 0, 'psel': 1, 'penable': 1, 'pwrite': 1,\
                            'paddr': 0, 'pwdata': 0, 'pready': 1, 'prdata': 00000000}

        # setting clock value
        self.clock = clock
        self.last_transaction = {}

        self.expected_memory = np.zeros(64)
        #print("array is",self.expected_memory)
        self.output = []
        self.expected_output = []
        self.expected_transaction = []

        # monitor initialization
        self.monitor = Monitor1(self, self.dut, name, clock, callback=None)
        #scoreboard for comparision of actual and expected output 
        self.scoreboard = Scoreboard(self.dut)

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
    
    def apb_slave_model(self,transaction):
        self.expected_transaction = {'pclk': 1, 'preset': 0, 'psel': 1, 'penable': 1, 'pwrite': 1,\
                                     'paddr': 0, 'pwdata': 0, 'pready': 1, 'prdata': 00000000}
        
        self.expected_transaction['pclk'] = transaction['pclk']
        self.expected_transaction['preset'] = transaction['preset']
        self.expected_transaction['psel'] = transaction['psel']
        self.expected_transaction['penable'] = transaction['penable']
        self.expected_transaction['pwrite'] = transaction['pwrite']
        self.expected_transaction['paddr'] = transaction['paddr']
        self.expected_transaction['pready'] = transaction['pready']

        if(int(transaction['pwrite'])==1):
            self.expected_memory[int(transaction['paddr'])-1] = int(transaction['pwdata'])
            self.expected_transaction['prdata'] = transaction['prdata']
        else:
            self.expected_output.append(self.expected_memory[int(transaction['paddr'])-1])
            self.expected_transaction['prdata'] = self.expected_memory[int(transaction['paddr'])-1]
    

@cocotb.test()
async def amba_apba_slave_basic_test(dut):
    """Basic Test"""
    #clock generator function called with 10 ns frequency
    clock = Clock(dut.pclk,10,units="ns")
    #clock started in parallel 
    cocotb.fork(clock.start())
    #object instantiation of slave test bench class
    tb = amba_apba_slave_tb(dut,"",clock=dut.pclk)
    await tb.resetseq()
    await tb.write(5,10)
    await tb.write(11,20)
    await tb.write(13,30)
    await tb.read(5)
    #Reads the value from the given value
    await tb.read(1)
    await tb.read(11)
    print("expected memory is",tb.expected_memory)
