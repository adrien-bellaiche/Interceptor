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


def fpgaRead(addr):
    """
    read and return FPGA register content (one byte)
    input:
        addr : address of the register relatively to the beginning 
               FPGA memory address
    output:
        v : register content
    """
    checkRunningOnJog()
    if jogio_utils.robotPlatform == "JOG":
        v = jogFpgaRead(addr)
    else:
        v = vjogFpgaRead(addr)
    return v


def fpgaWrite(addr, v):
    """
    write a value (byte) in a FPGA register, returning nothing
    input:
        addr : address of the register relatively to the beginning 
               FPGA memory address
        v :  8 bits value (byte) to write in the register 
    """
    checkRunningOnJog()
    if jogio_utils.robotPlatform == "JOG":
        jogFpgaWrite(addr, v)
    else:
        vjogFpgaWrite(addr, v)


def i2cRead(addr, register, debug=False):
    """
    read value from a register at a given i2c address and return a byte
    input:
         addr : address on the i2c bus
         register : register number 
         debug : displaying debug messages if True (not used yet)
    output:
         v : register content
    """
    checkRunningOnJog()
    if jogio_utils.robotPlatform == "JOG":
        v = jogI2cRead(addr, register, debug)
    else:
        v = vjogI2cRead(addr, register, debug)
    return v


def i2cWrite(addr, register, value, debug=False):
    """
    write a byte value in a register at a given i2c address, nothing returned
    input: 
         addr : address on the i2c bus
         register : register number 
         value : byte value to write in register
         debug : displaying debug messages if True (not used yet)
    """
    checkRunningOnJog()
    if jogio_utils.robotPlatform == "JOG":
        jogI2cWrite(addr, register, value, debug)
    else:
        vjogI2cWrite(addr, register, value, debug)


def deviceInit():
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
    checkRunningOnJog()
    if jogio_utils.robotPlatform == "JOG":
        v = jogDeviceInit()
    else:
        v = vjogDeviceInit()


def deviceRead(devFile):
    """
    reading value v on device file devFile
    input:
       devFile :  device file name
    output:
       v : short integer value (16 bits)
    not implemented yet on vJOG
    """
    checkRunningOnJog()
    if jogio_utils.robotPlatform == "JOG":
        v = jogDeviceRead(devFile)
    else:
        v = vjogDeviceRead(devFile)
    return v


def deviceWrite(devFile, v):
    """
    writing value v on device file devFile, returning nothing
    input:
       devFile :  device file name
    output:
       v : short integer value (16 bits)
    not implemented yet on vJOG
    """
    checkRunningOnJog()
    if jogio_utils.robotPlatform == "JOG":
        jogDeviceWrite(devFile, v)
    else:
        vjogDeviceWrite(devFile, v)


def fullStop():
    """
    full stop JOG (or vJOG), returning nothing
    """
    checkRunningOnJog()
    if jogio_utils.robotPlatform == "JOG":
        jogFullStop()
    else:
        vjogFullStop()
