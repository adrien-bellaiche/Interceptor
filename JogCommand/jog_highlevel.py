from JogCommand.jogio import *
from JogCommand.jogio_cmd_motors import *
from math import copysign, pi
import time


# leds, set and get
def set_led(v):
    """
    Set LED register with value in v
    if bit 0 is set LED D1 is on 
    if bit 1 is set LED D2 is on 
    if bit 2 is set LED D3 is on 
    if bit 3 is set LED D4 is on 
    """
    fpga_leds_addr = 0x18
    vl = v & 0x0f
    fpga_write(fpga_leds_addr, vl)


def get_leds():
    """
    Return the value of the LED register
    """
    fpga_leds_addr = 0x18
    vl = fpga_read(fpga_leds_addr)
    return vl & 0x0f


# compass, low resolustion (8 bits) and high resolution (0.1 degree)
def compass_lowres():
    """
    Get the value of the compass in low resolution mode
    The value is on 8 bits (resolution 1.4 degree)
    """
    i2c_compass_addr = 0x60
    compass_lowres_register = 0x01
    v = i2c_read(i2c_compass_addr, compass_lowres_register)
    return (round(v * 360.0 * 100.0 / 256)) / 100.0


def compass_highres():
    """
    Get the value of the compass in high resolution mode
    The resolution is 0.1 degree
    """
    i2c_compass_addr = 0x60
    compass_highres_register_less = 0x03
    compass_highres_register_most = 0x02
    vl = i2c_read(i2c_compass_addr, compass_highres_register_less)
    vh = i2c_read(i2c_compass_addr, compass_highres_register_most)
    return 0.1 * (vl + vh * 256.0)


# accessing sonars , all 5 simultaneously or individually by number (1 to 5)
# 1: left, 2: mid left, 3: center, 4: mid right, 5:right

def sonar_all():
    """ 
    Acquire the distance to first obstacle on 5 sonars simultaneously
    Distances in cm are returned in a 5 elements array s
    s[0] : sonar left
    s[1] : sonar mid left
    s[2] : sonar center
    s[3] : sonar mid right
    s[4] : sonar rigth
    """
    i2c_sonar_addr_base = 0x71
    sonar_cmd_register = 0x00
    sonar_range_register_less = 0x03
    sonar_range_register_most = 0x02
    sonar_setup_range_in_meter = 0x51
    # start acquisition
    for i in range(5):
        i2c_write(i2c_sonar_addr_base + i, sonar_cmd_register, sonar_setup_range_in_meter)
    # wait ... to ways travel time of ultrasonic wave
    time.sleep(0.075)
    # read data
    s = []
    for i in range(5):
        vl = i2c_read(i2c_sonar_addr_base + i, sonar_range_register_less)
        vh = i2c_read(i2c_sonar_addr_base + i, sonar_range_register_most)
        s.append(vl + 256.0 * vh)
    return s


# single sonar sNum (1 to 5)
def sonar_single(snum):
    """ 
    Acquire the distance to first obstacle on a single  sonar
    sNum, the sonar's number is defined as :
    0 : sonar left
    1 : sonar mid left
    2 : sonar center
    3 : sonar mid right
    4 : sonar rigth
    """
    i2c_sonar_addr_base = 0x71
    sonar_cmd_register = 0x00
    sonar_range_register_less = 0x03
    sonar_range_register_most = 0x02
    sonar_setup_range_in_meter = 0x51
    #print "set sonar cmd",sNum
    i2c_write(i2c_sonar_addr_base + snum - 1, sonar_cmd_register, sonar_setup_range_in_meter)
    time.sleep(0.075)
    #print "get sonar data",sNum
    vl = i2c_read(i2c_sonar_addr_base + snum - 1, sonar_range_register_less)
    vh = i2c_read(i2c_sonar_addr_base + snum - 1, sonar_range_register_most)
    s = vl + 256.0 * vh
    return s


# infrareds (converted by ADC) 
# all simultaneously or individualy ('left','right','front','rear')
def infrared__all():
    """
    Get reflectance value (expressed in mV) on the 4 infrared sensors
    The values are return in a 4 elements array v defined as
    v[0] : front infrared
    v[1] : left infrared
    v[2] : right infrared
    v[3] : rear infrared
    """
    device_write('/sys/bus/spi/devices/spi0.0/setup', 0x62)
    device_write('/sys/bus/spi/devices/spi0.0/averaging', 0x3c)
    device_write('/sys/bus/spi/devices/spi0.0/conversion', 0xb9)
    v = [device_read('/sys/bus/spi/devices/spi0.0/in6_input'),
         device_read('/sys/bus/spi/devices/spi0.0/in4_input'),
         device_read('/sys/bus/spi/devices/spi0.0/in5_input'),
         device_read('/sys/bus/spi/devices/spi0.0/in2_input')]
    return v


def infrared_single(side):
    """
    Get reflectance value (expressed in mV) on a given infrared sensors
    side defines which sensor is used
    side == "front" : front infrared
    side == "left": left infrared
    side == "right" : right infrared
    side == "rear" : rear infrared
    """
    device_write('/sys/bus/spi/devices/spi0.0/setup', 0x62)
    device_write('/sys/bus/spi/devices/spi0.0/averaging', 0x3c)
    device_write('/sys/bus/spi/devices/spi0.0/conversion', 0xb9)
    if side == "front":
        v = device_read('/sys/bus/spi/devices/spi0.0/in6_input')
    elif side == "left":
        v = device_read('/sys/bus/spi/devices/spi0.0/in4_input')
    elif side == "right":
        v = device_read('/sys/bus/spi/devices/spi0.0/in5_input')
    elif side == "rear":
        v = device_read('/sys/bus/spi/devices/spi0.0/in2_input')
    else:
        v = 0
    return v


# temperature in ADC chip
def temperature_adc():
    """ 
    return the temperature (in degrees) measure by ADC chip
    """
    v = device_read('/sys/bus/spi/devices/spi0.0/temp1_input')
    return float(v) / 1000.0


# adcPrintStatus , showimg content of setup, averaging and conversion registers
def adc_print_tatus():
    """
    display values in ADC registers (for debug purpose)
    """
    print "ADC Status -------------------------------------------"
    setup = device_read('/sys/bus/spi/devices/spi0.0/setup')
    conversion = device_read('/sys/bus/spi/devices/spi0.0/conversion')
    averaging = device_read('/sys/bus/spi/devices/spi0.0/averaging')
    print "ADC Setup register : %3d (0x%2.2x)" % (setup, setup)
    print "ADC Conversion register : %3d (0x%2.2x)" % (conversion, conversion)
    print "ADC Averaging register : %3d (0x%2.2x)" % (averaging, averaging)
    print "------------------------------------------------------"


def set_heading_simple(head):
    head_ok = False
    err_max = 10
    motors_set_direction(-1, 1)
    motors_set_speed(50, 50)
    while not head_ok:
        head_mes = compass_highres()
        head_err = abs(head - head_mes)
        if head_err < err_max:
            head_ok = True
            motors_set_speed(0, 0)
        else:
            time.sleep(0.1)


def set_heading(head):
    head_ok = False
    err_max = 0.5
    while not head_ok:
        head_mes = compass_highres()
        head_err = ((head_mes - head + 180) % 360) - 180
        side = copysign(1, head_err)
        motors_set_direction(-side, side)
        motors_set_speed(int(25 + 10 * head_err / 180), int(25 + 10 * head_err / 180))
        if abs(head_err) < err_max:
            head_ok = True
        else:
            time.sleep(0.1)
    motors_set_speed(0, 0)


def go_line_heading(head, speed, duration):
    set_heading(head)
    initime = time.time()
    motors_set_direction(1, 1)
    while (time.time() - initime) < duration:
        head_mes = compass_highres()
        head_err = ((head_mes - head + 180) % 360) - 180
        p = [speed * (1 - head_err / 20), speed * (1 + head_err / 20)]
        motors_set_speed(p[0], p[1])
        time.sleep(0.01)
    motors_set_speed(0, 0)


def get_odometry():
    """
    :return: [leftOdometer, rightOdometer]
    """
    p = [fpga_read(0x22), fpga_read(0x20)]

    for _ in [0, 1]:
        if p[_] + get_odometry.count[_]*65535 < (get_odometry.odos[_] - 5000):
            get_odometry.count[_] += 1
    get_odometry.odos = [p[_] + get_odometry.count[_]*65535 for _ in [0, 1]]
    return get_odometry.odos
get_odometry.count = [0, 0]
get_odometry.odos = [fpga_read(0x22), fpga_read(0x20)]

def get_theta():
    mag_ori = compass_highres()
    return mag_ori*2*pi/360

# unitary tests of JOG's sensors and actuators

if __name__ == "__main__":
    device_init()
    #setHeadingSimple(10)
    go_line_heading(180, 70, 10)
    time.sleep(100)
#
#    # leds
#    ledsSet (9)
#    print "leds : %x"%(ledsGet())
#    time.sleep(1)
#    ledsSet (6)
#    print "leds : %x"%(ledsGet())
#    time.sleep(1)
#    ledsSet (0)
#    print "leds : %x"%(ledsGet())
#
#    # compass
#    print "Compass LR : %6.1f"%(compassLowRes())
#    print "Compass HR : %6.1f"%(compassHighRes())
#    time.sleep(2)
#
#    # sonars
#    allson=sonarAll()
#    print "All sonars : %5.1f %5.1f %5.1f %5.1f %5.1f"%(allson[0],allson[1],
#                                                        allson[2],allson[3],
#                                                        allson[4])
#    print "Sonar Left      : %5.1f"%(sonarSingle(1))
#    print "Sonar Mid Left  : %5.1f"%(sonarSingle(2))
#    print "Sonar Center    : %5.1f"%(sonarSingle(3))
#    print "Sonar Mid Right : %5.1f"%(sonarSingle(4))
#    print "Sonar Right     : %5.1f"%(sonarSingle(5))
#    time.sleep(1)
#
#
#
#    # infrareds and temperature
# init ADC (load driver module and setup)
#
#    infrall = infraredAll()
#    print "ADC chip Temperature : %f"%(temperatureAdc())
#    print "Infrareds : ",infrall
#    time.sleep(0.2)
#    print "Infrared Front : %4d "%(infraredSingle('front'))
#    time.sleep(0.2)
#    print "Infrared Left  : %4d "%(infraredSingle('left'))
#    time.sleep(0.2)
#    print "Infrared Right : %4d "%(infraredSingle('right'))
#    time.sleep(0.2)
#    print "Infrared Rear  : %4d "%(infraredSingle('rear'))
#    time.sleep(0.2)
#    adcPrintStatus()
#
#    print "Sonar Center    : %5.1f"%(sonarSingle(3))
#    for i in range(15):
#        print "Sonar Center    : %5.1f"%(sonarSingle(3))
#        ledsSet (i+1)
#        time.sleep(4)
#
#    jogio.fullStop()