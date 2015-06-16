# low level IO Interface for JOG robot
#
# provides low level IO for both JOG and VJOG
#
# low level IO controls :
# - I2C bus (sonar, compass)
# - FPGA memory registers (leds, motors, odometers)
# - linux drivers files (infrared, temperature)
#

import platform
import ctypes
import time
import mmap
import os



robotPlatform = ""  # unset at start , after init either JOG or vJOG
#vFpgaRegs = array.array('c')  # virtual FPGA registers
#vI2cBus = [] # virtual I2C bus
# virtual device files
vDevFilesPath = {'init': False, 'setup': 0, 'conversion': 0, 'averaging': 0,
                 'in0_input': 0, 'in1_input': 0, 'in2_input': 0, 'in3_input': 0,
                 'in4_input': 0, 'in5_input': 0, 'in6_input': 0, 'in7_input': 0,
                 'temp1_input': 0}


# getting informations on computer
def get_platform_info():
    nbits, binary = platform.architecture()
    machine = platform.machine()
    name = platform.node()
    infos = {'nbits': nbits, 'binary': binary,
             'machine': machine, 'name': name}
    return infos


# running on JOG ? or on vJOG ?
def check_running_onjog():
    global robotPlatform
    if robotPlatform == "":
        robotPlatform = "vJOG"
        infos = get_platform_info()
        print infos
        if (infos['nbits'] == '32bit') and (infos['machine'] == 'armv5tejl'):
            robotPlatform = "JOG"
        else:
            print "init vJOG"
            from multiprocessing import Process, Manager
            from Jog_Utils import vjog
            # shared namespace
            global ns, simuProc, sharedRegs, changeRegs
            manager = Manager()
            ns = manager.Namespace()
            sharedRegs = manager.dict()
            changeRegs = manager.list()
            for i in (4, 6, 8, 0xa, 0xc, 0xe, 0x18, 0x20, 0x22):  # init FPGA regs
                st_reg = "fpga_0x%2.2x" % i
                reg_val = 0
                sharedRegs[st_reg] = reg_val
            # init I2C regs
            for i in range(4):
                st_reg = "fpga_0x60_%2.2x" % i
                sharedRegs[st_reg] = reg_val
            i2caddr = 7 * 16 + 1
            for a in range(5):
                for i in range(4):
                    st_reg = "fpga_0x%2.2x_%2.2x" % (i2caddr + a, i)
                    sharedRegs[st_reg] = reg_val

            for key in vDevFilesPath.keys():  # ADC device files
                st_reg = "dev_%s" % key
                sharedRegs[st_reg] = vDevFilesPath[key]

            sharedRegs['none'] = 'none'

            ns.alive = True
            ns.endOfInit = False
            simuProc = Process(target=vjog.simu, args=(ns, sharedRegs, changeRegs,))
            simuProc.start()
            while not ns.endOfInit:
                print "wait for vJOG's init ..."
                time.sleep(0.1)
            print "End of vJOG's initialization"
        print "robot platform is set to " + robotPlatform


# ------------------------------------------------------------------
# accessing FPGA registers on JOG

# read and return register content (one byte)
#    addr : address of the register relatively to the beginning 
#           FPGA address on ARMADEUS (Oxb6000000)
#           addr can be seen as register number  
def jog_fpga_read(addr):
    f = os.open("/dev/mem", os.O_RDONLY | os.O_SYNC)  # open memory device
    mem = mmap.mmap(f, 8192, mmap.MAP_SHARED,  # map register at
                    mmap.PROT_READ, 0, 0xd6000000)  # 0xd6000000 address
    mem.seek(addr)  # moving to register address
    vl = ord(mem.read_byte())  # reading one char and casting to byte
    mem.seek(addr + 1)  # moving to register address
    vh = ord(mem.read_byte())  # reading one char and casting to byte
    mem.close()  # close all ...
    os.close(f)
    v = vl + 256 * vh
    return v


# write a value (byte) in a register, returning nothing
#    addr : address of the register
#    v : 8 bits value (byte) to write in the register 
def jog_fpga_write(addr, v):
    f = os.open("/dev/mem", os.O_RDWR)  # open memory device
    mem = mmap.mmap(f, 8192, mmap.MAP_SHARED,  # and ap it
                    mmap.PROT_READ | mmap.PROT_WRITE, 0, 0xd6000000)
    mem.seek(addr)  # moving to address
    mem.write(chr(v))  # write byte data as char
    mem.seek(addr + 1)  # moving to address
    mem.write(chr(0))  # write byte data as char
    mem.close()  # close all ...
    os.close(f)


# emulating access to FPGA registers on VJOG
def vjog_fpga_read(addr):
    global ns, sharedRegs, changeRegs
    st_reg = "fpga_0x%2.2x" % addr
    return sharedRegs[st_reg]


def vjog_fpga_write(addr, v):
    global ns, sharedRegs, changeRegs
    st_reg = "fpga_0x%2.2x" % addr
    changeRegs.append((st_reg, v))
    sharedRegs[st_reg] = v
    #print "vjogFpgaWrite",addr,v,ord(vFpgaRegs[addr]),sharedRegs[st_reg]


# ------------------------------------------------------------------
# i2c stuff 

# defining structure of i2C messages
class I2cMsg(ctypes.Structure):
    """<linux/i2c-dev.h> struct i2c_msg"""

    _fields_ = [
        ('addr', ctypes.c_uint16),
        ('flags', ctypes.c_ushort),
        ('len', ctypes.c_short),
        ('buf', ctypes.POINTER(ctypes.c_char))]

    __slots__ = [name for name, type in _fields_]

# i2c_msg flags
I2C_M_TEN = 0x0010  # this is a ten bit chip address
I2C_M_WR = 0x0000  # write data ????
I2C_M_RD = 0x0001  # read data, from slave to master
I2C_M_NOSTART = 0x4000  # if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_REV_DIR_ADDR = 0x2000  # if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_IGNORE_NAK = 0x1000  # if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_NO_RD_ACK = 0x0800  # if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_RECV_LEN = 0x0400  # length will be first received byte


# /usr/include/linux/i2c-dev.h: 155
class I2cRdwrIoctlData(ctypes.Structure):
    """<linux/i2c-dev.h> struct i2c_rdwr_ioctl_data"""
    _fields_ = [
        ('msgs', ctypes.POINTER(I2cMsg)),
        ('nmsgs', ctypes.c_int)]

    __slots__ = [name for name, type in _fields_]


I2C_FUNC_I2C = 0x00000001
I2C_FUNC_10BIT_ADDR = 0x00000002
I2C_FUNC_PROTOCOL_MANGLING = 0x00000004  # I2C_M_NOSTART etc.


# ioctls
I2C_SLAVE = 0x0703  # Change slave address
# Attn.: Slave address is 7 or 10 bits
I2C_SLAVE_FORCE = 0x0706  # Change slave address
# Attn.: Slave address is 7 or 10 bits
# This changes the address, even if it
# is already taken!
I2C_TENBIT = 0x0704  # 0 for 7 bit addrs, != 0 for 10 bit
I2C_FUNCS = 0x0705  # Get the adapter functionality
I2C_RDWR = 0x0707  # Combined R/W transfer (one stop only)


# translate msg to ioctl input
def i2c_ioctl_msg(*msgs):
    msg_count = len(msgs)
    msg_array = (I2cMsg * msg_count)(*msgs)
    return msg_array, msg_count


# read value from a register at a given i2c address and return a byte
#    addr : address on the i2c bus
#    register : register number 
#    i2cDebug : displaying debug messages if true (not used yet)
def jog_i2c_read(addr, register, debug):
    import fcntl
    import posix

    n_i2c = 0
    f_i2c = posix.open("/dev/i2c-%i" % (n_i2c), posix.O_RDWR)

    flags = I2C_M_WR
    buf = ctypes.create_string_buffer(1)
    buf[0] = chr(register)
    msgs = I2cMsg(addr=addr, flags=flags, len=ctypes.sizeof(buf), buf=buf)
    msg_array, msg_count = i2c_ioctl_msg(msgs)
    io_i2c = I2cRdwrIoctlData(msgs=msg_array, nmsgs=msg_count)
    i2c_stat = fcntl.ioctl(f_i2c, I2C_RDWR, io_i2c)

    msgs.flags = I2C_M_RD
    msg_array, msg_count = i2c_ioctl_msg(msgs)
    io_i2c = I2cRdwrIoctlData(msgs=msg_array, nmsgs=msg_count)
    i2c_stat = fcntl.ioctl(f_i2c, I2C_RDWR, io_i2c)

    posix.close(f_i2c)
    return ord(buf[0])


#  write a byte value in a register at a given i2c address, nothing returned
#    addr : address on the i2c bus
#    register : register number
#    value : byte value to write  
#    debug : displaying debug messages if true (not used yet)
def jog_i2c_write(addr, register, value, debug):
    import fcntl
    import posix

    n_i2c = 0
    f_i2c = posix.open("/dev/i2c-%i" % n_i2c, posix.O_RDWR)

    flags = I2C_M_WR
    buf = ctypes.create_string_buffer(2)
    buf[0] = chr(register)
    buf[1] = chr(value)
    msgs = I2cMsg(addr=addr, flags=flags, len=ctypes.sizeof(buf), buf=buf)
    msg_array, msg_count = i2c_ioctl_msg(msgs)
    io_i2c = I2cRdwrIoctlData(msgs=msg_array, nmsgs=msg_count)
    i2c_stat = fcntl.ioctl(f_i2c, I2C_RDWR, io_i2c)

    posix.close(f_i2c)


# accessing I2C bus for VJOG

# read value from a register at a given i2c address and return a byte
#    addr : address on the i2c bus
#    register : register number 
#    i2cDebug : displaying debug messages if true (not used yet)
def vjog_i2c_read(addr, register, debug):
    global ns, sharedRegs, changeRegs
    st_reg = "i2c_0x%2.2x_%2.2d" % (addr, register)
    v = sharedRegs[st_reg]
    #print __name__, ",",vjogI2cRead.__name__ ,",", st_reg,",",v
    return v


# check is useless now, as vjog initializes the shared registers
def vjog_i2c_read_check(addr, register, debug):
    global ns, sharedRegs, changeRegs
    st_reg = "i2c_0x%2.2x_%2.2d" % (addr, register)
    try:
        v = sharedRegs[st_reg]
        print __name__, ",", vjog_i2c_read.__name__, ",", st_reg, ",", v
    except Exception:
        v = 0
        vjog_i2c_write(addr, register, v, debug)
    return v


#  write a byte value in a register at a given i2c address, nothing returned
#    addr : address on the i2c bus
#    register : register number
#    value : byte value to write  
#    debug : displaying debug messages if true (not used yet)
def vjog_i2c_write(addr, register, value, debug):
    global ns, sharedRegs, changeRegs
    st_reg = "i2c_0x%2.2x_%2.2d" % (addr, register)
    changeRegs.append((st_reg, value))
    sharedRegs[st_reg] = value


# ------------------------------------------------------------------
# ADC stuff

# Infrared et temperature sensing is done by a MAX 1027 analog to 
# digital converter

# deviceInit
# adc and temp uses device files created when the driver module is loaded
# before using ADC , the driver module (max1027) must be loaded using the 
# following command :
#     modprobe max1027
# on virtual JOG

# jogDeviceInit
def jog_device_init():
    # check if driver module for MAX1027 ADC is loaded
    print "check if driver module for MAX1027 ADC is loaded"
    try:
        with open('/sys/bus/spi/devices/spi0.0/setup'):
            pass
    except IOError:
        os.system('modprobe max1027')
        time.sleep(0.25)


# vjogDeviceInit
def vjog_device_init():
    global ns, sharedRegs, changeRegs
    dev_file_tag = 'init'
    st_reg = "dev_%s" % dev_file_tag
    sharedRegs[st_reg] = True
    changeRegs.append((st_reg, True))


# jogDeviceRead
def jog_device_read(dev_file):
    #print "read ",devFile
    f = open(dev_file, "r")
    v = f.read()
    if v[0:2] == "0x":
        v = int(v, 16)
    else:
        v = int(v)
    f.close()
    return v


# vjogDeviceRead
def vjog_device_read(dev_file):
    global ns, sharedRegs, changeRegs
    s = dev_file.split('/')
    dev_file_tag = s[len(s) - 1]
    st_reg = "dev_%s" % dev_file_tag
    return sharedRegs[st_reg]


# jogDeviceWrite
def jog_device_write(dev_file, v):
    f = open(dev_file, "w")
    f.write(str(v))
    f.close()


# vjogDeviceWrite
def vjog_device_write(dev_file, v):
    global ns, sharedRegs, changeRegs
    s = dev_file.split('/')
    dev_file_tag = s[len(s) - 1]
    st_reg = "dev_%s" % dev_file_tag
    #print __name__, ",",vjogI2cRead.__name__ ,",", st_reg
    sharedRegs[st_reg] = v
    changeRegs.append((st_reg, v))


# full stop JOG 
def jog_full_stop():
    jog_fpga_write(0x18, 0)  # reset FPGA


def vjog_full_stop():
    global ns
    ns.alive = False
    #print ns
    #print sharedRegs
    #print changeRegs
    simuProc.join()