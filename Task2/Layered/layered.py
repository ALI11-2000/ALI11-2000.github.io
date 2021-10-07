import logging
import cocotb
from cocotb import clock
from cocotb.triggers import Event, FallingEdge, RisingEdge, Timer
import random

from cocotb.result import TestFailure

from cocotb_bus.monitors import BusMonitor
from cocotb_bus.drivers import BusDriver
from cocotb_bus.scoreboard import Scoreboard
from cocotb.clock import Clock
from cocotb.binary import BinaryValue
import logging


class sq_root_Monitor (BusMonitor):
    # monitor to be used at input and output of the DUT
    def __init__(self, entity, name, clock, reset=None, reset_n=None, callback=None, event=None, bus_separator="_"):
        # Bus monitor initalized
        BusMonitor.__init__(self, entity, name, clock, reset, reset_n, callback, event, bus_separator)
        # check for duplicate sampling
        self.last_Transaction = None

    # function used to tell when to sample transactions
    @cocotb.coroutine
    async def _monitor_recv(self):
        await Timer(1)
        while (True):
            await RisingEdge(self.clock)
            transaction = dict(self.bus.capture())
            #print("in monitor we have",transaction)
            if(self.name == 'i'):
                if int(transaction['ready']) == 1 :
                    self._recv(transaction)
                    print("Input sampled is",int(self.entity.i_num))
            else:
                if int(transaction['done']) == 1 :
                    self._recv(transaction)
                    print("Output sampled is",int(self.entity.o_res))
            
class sq_root_OMonitor(sq_root_Monitor):
    # Output monitor sampling the output signals 
    _signals = {"res","done"}
    
    def __init__(self, entity, name, clock, reset=None, reset_n=None, callback=None, event=None, bus_separator = "_"):
        sq_root_Monitor.__init__(self, entity, name, clock, reset, reset_n, callback, event, bus_separator)
        print("Output Monitor Starting")

class sq_root_IMonitor(sq_root_Monitor):
    # Input monitor sampling the input signal
    _signals = {"num","ready"}

    def __init__(self, entity, name, clock, reset=None, reset_n=None, callback=None, event=None, bus_separator = "_"):
        sq_root_Monitor.__init__(self, entity, name, clock, reset, reset_n, callback, event, bus_separator)
        print("Input monitor starting")

class sq_root_Driver(BusDriver):
    _signals = ["num", "ready"]

    def __init__(self, entity, name, clock):
        BusDriver.__init__(self, entity, name,clock)
        self.bus.num.setimmediatevalue(0)
        self.bus.ready.setimmediatevalue(0)
        self.clk = clock
    
    @cocotb.coroutine
    async def send_input(self, x):
        self.bus.num <= x
        self.bus.ready <= 1
        await RisingEdge(self.clk)
        self.bus.ready <= 0
        await FallingEdge(self.entity.o_done)

class sq_root__tb(object):
    def __init__(self,dut):
        self.dut = dut
        # input driver initialized
        self.input_drv = sq_root_Driver(dut,"i",clock=self.dut.clk)
        # input monitor initialized
        self.input_mon = sq_root_IMonitor(dut,"i",clock=self.dut.clk,callback = self.sq_root__model)
        # output monitor initialized
        self.output_mon = sq_root_OMonitor(dut,"o",clock=self.dut.clk)
        # expected output empty array declared
        self.expected_output = []
        # scoreboard initialized
        self.scoreboard = Scoreboard(dut)
        # output monitor and expected output added to the scoreboard to be compared
        self.scoreboard.add_interface(self.output_mon, self.expected_output)

    # sq_root_ reference model which will be called by the input monitor when input is sampled
    def sq_root__model(self,transaction):
        self.eX = BinaryValue(int(int(self.dut.i_num)**0.5))
        print("Transaction Model Called with expected output",int(self.eX),"for",int(self.dut.i_num))
        # expected value added in the expected output array
        self.expected_output.append({'done':1,'res':self.eX})

    


@cocotb.test()
async def sq_root__basic_test(dut):
    """Basic Test"""
    clock = Clock(dut.clk,10,units="ns")
    cocotb.fork(clock.start())
    for i in range(2):
        await cocotb.triggers.RisingEdge(dut.clk)
        dut.rst=1
    dut.rst=0
    tb = sq_root__tb(dut)
    await tb.input_drv.send_input(16)
    await tb.input_drv.send_input(81)
    raise tb.scoreboard.result