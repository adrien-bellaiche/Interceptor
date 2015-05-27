"""
 jogio module provides mid level IO Interface for JOG and vJOG robots

 checks if running on actual JOG robot 
 if not trying to run vJOG virtual robot

  mid level IO controls :
    - I2C bus (sonar, compass)
    - FPGA memory registers (leds, motors, odometers)
    - linux drivers files (infrared, temperature)

"""
from Jog_Utils import jogio_utils
from Jog_Utils.jogio_utils import *  # low level IO controls


def fpga_read(addr):
    """
    read and return FPGA register content (one byte)
    input:
        addr : address of the register relatively to the beginning 
               FPGA memory address
    output:
        v : register content
    """
    check_running_onjog()
    if jogio_utils.robotPlatform == "JOG":
        v = jog_fpga_read(addr)
    else:
        v = vjog_fpga_read(addr)
    return v


def fpga_write(addr, v):
    """
    write a value (byte) in a FPGA register, returning nothing
    input:
        addr : address of the register relatively to the beginning 
               FPGA memory address
        v :  8 bits value (byte) to write in the register 
    """
    check_running_onjog()
    if jogio_utils.robotPlatform == "JOG":
        jog_fpga_write(addr, v)
    else:
        vjog_fpga_write(addr, v)


def i2c_read(addr, register, debug=False):
    """
    read value from a register at a given i2c address and return a byte
    input:
         addr : address on the i2c bus
         register : register number 
         debug : displaying debug messages if True (not used yet)
    output:
         v : register content
    """
    check_running_onjog()
    if jogio_utils.robotPlatform == "JOG":
        v = jog_i2c_read(addr, register, debug)
    else:
        v = vjog_i2c_read(addr, register, debug)
    return v


def i2c_write(addr, register, value, debug=False):
    """
    write a byte value in a register at a given i2c address, nothing returned
    input: 
         addr : address on the i2c bus
         register : register number 
         value : byte value to write in register
         debug : displaying debug messages if True (not used yet)
    """
    check_running_onjog()
    if jogio_utils.robotPlatform == "JOG":
        jog_i2c_write(addr, register, value, debug)
    else:
        vjog_i2c_write(addr, register, value, debug)


def device_init():
    """
    Initializing ADC linux device driver (no parameters)
    ADC and temperature uses device files created when the driver module 
    is loaded.
    On actual JOG, before using ADC , the driver module (max1027) 
    must be loaded using the following command :
                  modprobe max1027
    On virtual JOG, ADC is not implemented yet ...
    """
    print "init ADC on " + jogio_utils.robotPlatform
    check_running_onjog()
    if jogio_utils.robotPlatform == "JOG":
        jog_device_init()
    else:
        vjog_device_init()


def device_read(dev_file):
    """
    reading value v on device file devFile
    input:
       devFile :  device file name
    output:
       v : short integer value (16 bits)
    not implemented yet on vJOG
    """
    check_running_onjog()
    if jogio_utils.robotPlatform == "JOG":
        v = jog_device_read(dev_file)
    else:
        v = vjog_device_read(dev_file)
    return v


def device_write(dev_file, v):
    """
    writing value v on device file devFile, returning nothing
    input:
       devFile :  device file name
    output:
       v : short integer value (16 bits)
    not implemented yet on vJOG
    """
    check_running_onjog()
    if jogio_utils.robotPlatform == "JOG":
        jog_device_write(dev_file, v)
    else:
        vjog_device_write(dev_file, v)


def full_stop():
    """
    full stop JOG (or vJOG), returning nothing
    """
    check_running_onjog()
    if jogio_utils.robotPlatform == "JOG":
        jog_full_stop()
    else:
        vjog_full_stop()
