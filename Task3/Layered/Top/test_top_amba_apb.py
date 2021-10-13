# importing required libraries
import cocotb
from cocotb.decorators import coroutine
from cocotb.triggers import Timer, Event, FallingEdge, RisingEdge
from cocotb.clock import Clock
from numpy import zeros
# importing layered testbench modules
from cocotb_bus.monitors import BusMonitor
from cocotb_bus.drivers import BusDriver
from cocotb_bus.scoreboard import Scoreboard


class amba_apb_driver (BusDriver):
    """
    AMBA APB bus driver class for driving top module inputs

    Args:
        dut: design under test
        clock: clock signal to be used by driver for triggers
    """

    # Input signals to be driven by the driver
    _signals = {"preset","transfer","mpwrite","apb_write_paddr", \
                "apb_write_data","apb_read_paddr"}
    
    def __init__(self, entity, clock):
        """Driver class constructor based on cocotb BusDriver class"""
        # Setting dut as a class object
        self.dut = entity
        # Setting clock as class object
        self.clock = clock
        # Bus driver class initialized
        BusDriver.__init__(self,entity,clock=clock,name="",bus_separator=None)
        # Set immediate values for the inputs signals
        self.bus.transfer.setimmediatevalue(0)
        self.bus.mpwrite.setimmediatevalue(0)
        self.bus.apb_write_paddr.setimmediatevalue(0)
        self.bus.apb_write_data.setimmediatevalue(0)
        self.bus.apb_read_paddr.setimmediatevalue(0)

    @cocotb.coroutine
    async def resetseq(self):
        """
        Driver Reset Sequence for resetting the top module
        
        Args:
            No Arguments required
        """
        await RisingEdge(self.clock)
        self.bus.preset <= 1 
        await RisingEdge(self.clock)
        self.bus.preset <= 0

    @cocotb.coroutine
    async def write(self, addr, data):
        """
        Driver Write sequence for writing given data at the
        address specified in the slave

        Args:
            addr: APB slave address for which data is to be 
                  written
            data: Data to be written in slave
        """
        self.bus.transfer <= 1
        self.bus.mpwrite <= 1
        self.bus.apb_write_paddr <= addr
        self.bus.apb_write_data <= data
        # wait for acknowledgenent from the slave for transaction completion
        await FallingEdge(self.dut.pready)
        self.bus.transfer <= 0

    
    @cocotb.coroutine
    async def read(self, addr):
        """
        Driver Read sequence for writing given data at the
        address specified in the slave

        Args:
            addr: APB slave address for which data is to be 
                  read
        """
        self.bus.transfer <= 1
        self.bus.mpwrite <= 0
        self.bus.apb_write_paddr <= addr
        # wait for acknowlegement from the slave for transaction completion
        await FallingEdge(self.dut.pready)
        self.bus.transfer <= 0


class amba_apb_monitor(BusMonitor):
    """
    AMBA APB bus monitor class for monitoring all signals

    Args:
        dut: design under test
        clock: clock signal to be used by driver for triggers
    """
    # monitor will be completed by tomorrow night




@cocotb.test()
async def top_amba_apb_test(dut):
    """CocoTB AMBA APB Layered Testbench"""
    # setting the clock signal using builtin cocotb function
    clock_signal = Clock(dut.pclk,10,"ns")
    # running clock signal in parallel with the test
    cocotb.fork(clock_signal.start())
    # APB test bench class object created
    tb = amba_apb_driver(dut,dut.pclk)
    # Resetting the design using the AMBA APB driver
    await tb.resetseq()
    # Writing 20 in the 10 address in slave
    await tb.write(10,20)
    # Reading Value from the 10 address in slave
    await tb.read(10)