import logging
import cocotb
from cocotb.triggers import Event, Timer
import random

from cocotb.result import TestFailure

from cocotb_bus.monitors import BusMonitor
from cocotb_bus.drivers import BusDriver
from cocotb_bus.scoreboard import Scoreboard

from cocotb.binary import BinaryValue

class AdderMonitor (BusMonitor):
    # monitor to be used at input and output of the DUT
    def __init__(self, entity, name, clock, reset=None, reset_n=None, callback=None, event=None, bus_separator="_"):
        BusMonitor.__init__(self, entity, name, clock, reset, reset_n, callback, event, bus_separator)

    @cocotb.coroutine
    def _monitor_recv(self):
        yield Timer(2)
        transaction = dict(self.bus.capture())
        self._recv(transaction)


class AdderOMonitor(AdderMonitor):
    # Output monitor sampling the output signals 
    _signals = {"X"}
    
    def __init__(self, entity, name, clock=None, reset=None, reset_n=None, callback=None, event=None, bus_separator = "_"):
        AdderMonitor.__init__(self, entity, name, clock, reset, reset_n, callback, event, bus_separator)
        print("Output Monitor Starting")

class AdderIMonitor(AdderMonitor):
    # Input monitor sampling the input signal
    _signals = {"A","B"}

    def __init__(self, entity, name, clock=None, reset=None, reset_n=None, callback=None, event=None, bus_separator = "_"):
        AdderMonitor.__init__(self, entity, name, clock, reset, reset_n, callback, event, bus_separator)
        print("Input monitor starting")

class AdderDriver(BusDriver):
    _signals = [ "A", "B"]

    def __init__(self, entity, name):
        BusDriver.__init__(self, entity, name,clock= None)
        self.bus.A.setimmediatevalue(0)
        self.bus.B.setimmediatevalue(0)

class adder_tb(object):
    def __init__(self,dut):
        self.dut = dut
        # input driver initialized
        self.input_drv = AdderDriver(dut,"i")
        # input monitor initialized
        self.input_mon = AdderIMonitor(dut,"i",callback = self.adder_model)
        # output monitor initialized
        self.output_mon = AdderOMonitor(dut,"o")
        # expected output empty array declared
        self.expected_output = []
        # scoreboard initialized
        self.scoreboard = Scoreboard(dut)
        # output monitor and expected output added to the scoreboard to be compared
        self.scoreboard.add_interface(self.output_mon, self.expected_output)

    # adder reference model which will be called by the input monitor when input is sampled
    def adder_model(self,transaction):
        self.eX = BinaryValue(int(self.dut.i_A)+int(self.dut.i_B))
        # expected value added in the expected output array
        self.expected_output.append({'X':self.eX})

    @cocotb.coroutine
    async def send_input(self, x, y):
        self.dut.i_A <= x
        self.dut.i_B <= y
        await Timer(3)


@cocotb.test()
async def adder_basic_test(dut):
    """Test for 5 + 10"""

    A = 5
    B = 10
    tb = adder_tb(dut)
    #await tb.start_input(1)
    await tb.send_input(A,B)
    await tb.send_input(12,13)
    await tb.send_input(14,15)
    raise tb.scoreboard.result