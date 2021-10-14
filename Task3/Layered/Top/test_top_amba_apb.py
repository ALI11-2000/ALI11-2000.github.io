# importing required libraries
from os import name
import cocotb
from cocotb.triggers import FallingEdge, RisingEdge
from cocotb.clock import Clock
from cocotb.handle import BinaryValue
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

    # Top Module signals to be sampled by monitor
    _signals = ["transfer","mpwrite","apb_write_paddr","apb_write_data" \
                ,"apb_read_paddr","prdata","apb_read_data_out","psel" \
                ,"penable","pready"]

    def __init__(self, entity, clock, expected):
        """Monitor Constructor based on BusMonitor Class"""
        BusMonitor.__init__(self,entity,clock=clock,name="",bus_separator=None)
        # clock set as a class object
        self.clock = clock
        # creating a reference memory module for reference model
        self.expected_memory = zeros(64)
        # creating the empy arrays to be compared
        self.output = []
        self.expected_output = expected


    def amba_apb_model(self,transaction):
        """APB Model for prediction of output transaction"""
        # In case of write operation write the data value in the reference memory for comparison
        # in read operation
        if(int(transaction['mpwrite'])==1):
            self.expected_memory[int(transaction['apb_write_paddr'])-1] = (int(transaction['apb_write_data']))
        # In case of read operation read the value from the expected memory for comparison with the 
        # actual output od the dut
        else:
            self.expected_output.append(int(self.expected_memory[int(transaction['apb_write_paddr'])-1]))
    
    @cocotb.coroutine
    async def _monitor_recv(self):
        """Monitor recieve is the recieving function that recieve values"""
        # wait for ready signal after reset
        await RisingEdge(self.bus.pready)
        # continuously running the monitor
        while (True):
            # wait for rising clock edge
            await RisingEdge(self.clock)
            # capture transaction at every rising clock edge
            transaction = dict(self.bus.capture())
            #print(transaction)
            #only sample transaction in the recieve function
            #when the slave has acknowledged the master for 
            #completion of transaction
            if int(self.bus.pready) == 1 :
                # calling the reference model for getting expected output
                self.amba_apb_model(transaction)
                # when read operation is performed save the result in output
                if((transaction['mpwrite']) == BinaryValue(0)):
                    # appending output data in the output array
                    self.output.append(int(transaction['prdata']))
                    self._recv(int(transaction['prdata']))
                """
                # Following block can be used in place of scoreboard
                # creating our own scoreboard so that the test does not stop
                # after an occurance of error
                if(str(self.output) != str(self.expected_output)):
                    self.log.error("Got %s but expected %s",self.output,self.expected_output)
                    self.log.error("Test failed for transaction %s",transaction)
                """
                
class amba_apb_tb(object):
    """
    AMBA APB layered testbench class
    """
    def __init__(self,dut,clock):
        """Testbench constructor based on dirver and monitor"""
        # setting up the driver
        self.driver = amba_apb_driver(dut,clock)
        # expected output used by the reference model and scoreboard
        self.expected = []
        # setting up the monitor
        self.monitor = amba_apb_monitor(dut,clock,self.expected)
        # setting up the scoreboard for completing test with Raising Test error at the end of simulation
        self.scoreboard = Scoreboard(dut,fail_immediately=False)
        # adding monitor in the scoreboard
        self.scoreboard.add_interface(self.monitor,self.expected,strict_type=False)

@cocotb.test()
async def top_amba_apb_test(dut):
    """CocoTB AMBA APB Layered Testbench"""
    # setting the clock signal using builtin cocotb function
    clock_signal = Clock(dut.pclk,10,"ns")
    # running clock signal in parallel with the test
    cocotb.fork(clock_signal.start())
    # APB test bench class object created
    tb = amba_apb_tb(dut,dut.pclk)
    # Resetting the design using the AMBA APB driver
    await tb.driver.resetseq()
    # Writing 20 in the 10 address in slave
    await tb.driver.write(10,20)
    # Reading Values from different addresses in slave
    await tb.driver.read(10)
    await tb.driver.read(2)
    # Raise error if scoreboard results are different
    raise tb.scoreboard.result