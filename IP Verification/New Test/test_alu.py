#importing required libraries
import cocotb
from cocotb import clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
from cocotb.handle import BinaryRepresentation
import random
import logging

from codecs import decode
import struct


def bin_to_float(b):
    """ Convert binary string to a float. """
    bf = int_to_bytes(int(b, 2), 8)  # 8 bytes needed for IEEE 754 binary64.
    return struct.unpack('>d', bf)[0]


def int_to_bytes(n, length):  # Helper function
    """ Int/long to byte string.

        Python 3.2+ has a built-in int.to_bytes() method that could be used
        instead, but the following works in earlier versions including 2.x.
    """
    return decode('%%0%dx' % (length << 1) % n, 'hex')[-length:]

#initiating cocotb test
@cocotb.test()
async def alu_test(dut):
    clk = clock.Clock(dut.clk,10,'ns')
    cocotb.fork(clk.start())
    dut.rst.value = 1
    dut.degrees.value = 90
    dut.actv.value = 0
    dut.enable.value = 1
    for i in range(1):await RisingEdge(dut.clk)
    dut.rst.value = 0
    for i in range(50): await RisingEdge(dut.clk)
    result = bin_to_float(str(dut.data1.value))
    print("input is ",(dut.degrees),"and sine output is ",(result))

    dut.actv.value = 1
    for i in range(50): await RisingEdge(dut.clk)
    result = bin_to_float(str(dut.data1.value))
    print("input is ",(dut.degrees),"and cosine output is ",(result))

    dut.actv.value = 2
    for i in range(50): await RisingEdge(dut.clk)
    result = bin_to_float(str(dut.data1.value))
    print("input is ",(dut.degrees),"and tangent output is ",(result))




#asserting error if the test fails
 #   assert dut.X.value == output1, "Randomised test failed with: {A} \
 #   {y}  {B} = {X} for {a}".format(A=dut.A.value, B=dut.B.value,     \
 #    X=dut.X.value,y=x[sel],a=output1)