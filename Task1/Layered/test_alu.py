import logging
import cocotb
from cocotb.triggers import Event, Timer
import random
#from alu_model import alu_model

from cocotb.result import TestFailure

from cocotb_bus.monitors import BusMonitor
from cocotb_bus.drivers import BusDriver
from cocotb_bus.scoreboard import Scoreboard

from cocotb.binary import BinaryValue

class AluMonitor (BusMonitor):
    # monitor to be used at input and output of the DUT
    def __init__(self, entity, name, clock=None, reset=None, reset_n=None, callback=None, event=None, bus_separator="_"):
        # Bus monitor initalized
        BusMonitor.__init__(self, entity, name, clock, reset, reset_n, callback, event, bus_separator)
        # check for duplicate sampling
        self.last_Transaction = None

    # function used to tell when to sample transactions
    @cocotb.coroutine
    async def _monitor_recv(self):
        while (True):
            await Timer(2)
            transaction = dict(self.bus.capture())
            # check if transaction duplicate or not
            # checks if input is sampled or output is
            if (self.name == 'i'):
                print("Input Sampled",transaction)
            else:
                print("Output Sampled",transaction)
            # transaction sampled by _recv
            self._recv(transaction)
            # updates last transaction
            self.last_Transaction = transaction


class AluOMonitor(AluMonitor):
    # Output monitor sampling the output signals 
    _signals = {"X"}
    
    def __init__(self, entity, name, clock=None, reset=None, reset_n=None, callback=None, event=None, bus_separator = "_"):
        AluMonitor.__init__(self, entity, name, clock, reset, reset_n, callback, event, bus_separator)
        print("Output Monitor Starting")

class AluIMonitor(AluMonitor):
    # Input monitor sampling the input signal
    _signals = {"A","B","sel"}

    def __init__(self, entity, name, clock=None, reset=None, reset_n=None, callback=None, event=None, bus_separator = "_"):
        AluMonitor.__init__(self, entity, name, clock, reset, reset_n, callback, event, bus_separator)
        print("Input monitor starting")

class AluDriver(BusDriver):
    _signals = [ "A", "B", "sel"]

    def __init__(self, entity, name):
        BusDriver.__init__(self, entity, name,clock= None)
        self.bus.A.setimmediatevalue(0)
        self.bus.B.setimmediatevalue(0)
        self.bus.sel.setimmediatevalue(0)

class alu_tb(object):
    def __init__(self,dut):
        self.dut = dut
        # input driver initialized
        self.input_drv = AluDriver(dut,"i")
        # input monitor initialized
        self.input_mon = AluIMonitor(dut,"i",callback = self.alu_model)
        # output monitor initialized
        self.output_mon = AluOMonitor(dut,"o")
        # expected output empty array declared
        self.expected_output = []
        # scoreboard initialized
        self.scoreboard = Scoreboard(dut)
        # output monitor and expected output added to the scoreboard to be compared
        self.scoreboard.add_interface(self.output_mon, self.expected_output)

    # alu reference model which will be called by the input monitor when input is sampled
  
    def alu_model(self,transaction):
    #ALU Model for simple arithmetic calculations
        a = int(self.dut.i_A)
        b = int(self.dut.i_B)
        sel = int(self.dut.i_sel)
        X=[a+b,abs(int(a-b)),a+b,(a) & (b), (a) | (b),(a) ^ (b),a,b]
        #Performing comparison between the two numbers
        if(sel==2):
            if(int(a)>int(b)):
                return 1
            else:
                return 0
        self.eX =BinaryValue(X[sel])
        self.expected_output.append({'X':self.eX})

    @cocotb.coroutine
    async def send_input(self, x, y, z):
        self.dut.i_A <= x
        self.dut.i_B <= y
        self.dut.i_sel <= z
        await Timer(3)


@cocotb.test()
async def alu_test(dut):
    """Basic Test"""

    tb = alu_tb(dut)
    await tb.send_input(2,3,0)
    await tb.send_input(12,13,1)
    await tb.send_input(2,3,1)
    await tb.send_input(14,15,1)
    raise tb.scoreboard.result