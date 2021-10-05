import logging
import cocotb
from cocotb import clock
from cocotb.decorators import coroutine
from cocotb.triggers import Event, FallingEdge, RisingEdge, Timer
import random
from cocotb.result import TestFailure
from cocotb_bus.monitors import BusMonitor
from cocotb_bus.drivers import BusDriver
from cocotb_bus.scoreboard import Scoreboard
from cocotb.clock import Clock
from cocotb.binary import BinaryValue
import logging



class sq_root__tb(BusDriver,BusMonitor):
    _signals = [
        "i_num","i_ready","o_res","o_done"
    ]

    def __init__(self,entity,name,clock):
        self.driver = BusDriver.__init__(self, entity, name, clock)
        self.monitor = BusMonitor.__init__(self, entity, name, clock)
        self.clock = clock
        self.bus.i_num.setimmediatevalue(0)
        self.bus.i_ready.setimmediatevalue(0)
        self.output = []
        self.expected_output = []
        self.scoreboard = Scoreboard(entity)
    
    @cocotb.coroutine
    async def resetseq(self):
        for i in range(2):
            await cocotb.triggers.RisingEdge(self.clock)
            self.bus.rst=1
        self.bus.rst=0

    @cocotb.coroutine
    async def send(self, num):
        await RisingEdge(self.clock)
        self.bus.i_num <= num
        self.bus.i_ready <= 1
        await RisingEdge(self.clock)
        self.bus.i_ready <= 0
        await FallingEdge(self.bus.o_done)
    
    @cocotb.coroutine
    async def _monitor_recv(self):
        await Timer(1)
        while (True):
            await RisingEdge(self.clock)
            transaction = dict(self.bus.capture())
            #print("in monitor we have",transaction)
            if int(self.bus.i_ready) == 1 :
                self._recv(transaction)
                print("Input sampled is",transaction)
                self.sq_root__model(self)
            else:
                if int(self.bus.o_done) == 1 :
                    self._recv(transaction)
                    print("Output sampled is",transaction)
                    self.output.append({'res':int(self.bus.o_res)})
                    self.scoreboard.compare(self.output,self.expected_output,log="Comparing results")
    
    def sq_root__model(self,transaction):
        self.eX = BinaryValue(int(int(self.bus.i_num)**0.5))
        print("Transaction Model Called with expected output",int(self.eX),"for",int(self.bus.i_num))
        # expected value added in the expected output array
        self.expected_output.append({'res':self.eX})


@cocotb.test()
async def sq_root__basic_test(dut):
    """Basic Test"""
    clock = Clock(dut.clk,10,units="ns")
    cocotb.fork(clock.start())
    tb = sq_root__tb(dut,name="",clock=dut.clk)
    await tb.resetseq()
    await tb.send(16)
    await tb.send(81)