import jogio
import time
import sys

# work to be done by students in UV 2.7 module 2 (2H+3H)

# leds, set and get
def ledsSet (v):
    """
    Set LED register with value in v
    if bit 0 is set LED D1 is on 
    if bit 1 is set LED D2 is on 
    if bit 2 is set LED D3 is on 
    if bit 3 is set LED D4 is on 
    """
    fpgaLedsAddr = 0x18
    vl = v & 0x0f
    jogio.fpgaWrite(fpgaLedsAddr,vl)

def ledsGet ():
    """
    Return the value of the LED register
    """
    fpgaLedsAddr = 0x18
    vl = jogio.fpgaRead(fpgaLedsAddr)
    return vl & 0x0f

# compass, low resolustion (8 bits) and high resolution (0.1 degree)
def compassLowRes ():
    """
    Get the value of the compass in low resolution mode
    The value is on 8 bits (resolution 1.4 degree)
    """
    i2cCompassAddr = 0x60
    compassLowResRegister = 0x01
    v = jogio.i2cRead(i2cCompassAddr,compassLowResRegister)
    return (round (v*360.0*100.0/256))/100.0

def compassHighRes():
    """
    Get the value of the compass in high resolution mode
    The resolution is 0.1 degree
    """
    i2cCompassAddr = 0x60
    compassHighResRegisterLess = 0x03
    compassHighResRegisterMost = 0x02
    vl = jogio.i2cRead (i2cCompassAddr,compassHighResRegisterLess)
    vh = jogio.i2cRead (i2cCompassAddr,compassHighResRegisterMost)
    return 0.1*(vl+vh*256.0)


# accessing sonars , all 5 simultaneously or individually by number (1 to 5)
#   1: left, 2: mid left, 3: center, 4: mid right, 5:right

def sonarAll():
    """ 
    Acquire the distance to first obstacle on 5 sonars simultaneously
    Distances in cm are returned in a 5 elements array s
    s[0] : sonar left
    s[1] : sonar mid left
    s[2] : sonar center
    s[3] : sonar mid right
    s[4] : sonar rigth
    """
    i2cSonarAddrBase = 0x71
    sonarCmdRegister = 0x00
    sonarRangeRegisterLess = 0x03
    sonarRangeRegisterMost = 0x02
    sonarSetupRangeInMeter = 0x51
    # start acquisition
    for i in range(5):
        jogio.i2cWrite(i2cSonarAddrBase+i,sonarCmdRegister,
                       sonarSetupRangeInMeter)
    # wait ... to ways travel time of ultrasonic wave
    time.sleep(0.075)
    # read data
    s = []
    for i in range(5):
        vl = jogio.i2cRead(i2cSonarAddrBase+i,sonarRangeRegisterLess)
        vh = jogio.i2cRead(i2cSonarAddrBase+i,sonarRangeRegisterMost)
        s.append (vl+256.0*vh)
    return s

# single sonar sNum (1 to 5)
def sonarSingle(sNum):
    """ 
    Acquire the distance to first obstacle on a single  sonar
    sNum, the sonar's number is defined as :
    0 : sonar left
    1 : sonar mid left
    2 : sonar center
    3 : sonar mid right
    4 : sonar rigth
    """
    i2cSonarAddrBase = 0x71
    sonarCmdRegister = 0x00
    sonarRangeRegisterLess = 0x03
    sonarRangeRegisterMost = 0x02
    sonarSetupRangeInMeter = 0x51
    #print "set sonar cmd",sNum
    jogio.i2cWrite(i2cSonarAddrBase+sNum-1,
                   sonarCmdRegister,
                   sonarSetupRangeInMeter)
    time.sleep(0.075)
    #print "get sonar data",sNum
    vl = jogio.i2cRead(i2cSonarAddrBase+sNum-1,sonarRangeRegisterLess)
    vh = jogio.i2cRead(i2cSonarAddrBase+sNum-1,sonarRangeRegisterMost)
    s = vl+256.0*vh
    return s

# infrareds (converted by ADC) 
#     all simultaneously or individualy ('left','right','front','rear')
def infraredAll():
    """
    Get reflectance value (expressed in mV) on the 4 infrared sensors
    The values are return in a 4 elements array v defined as
    v[0] : front infrared
    v[1] : left infrared
    v[2] : right infrared
    v[3] : rear infrared
    """
    jogio.deviceWrite('/sys/bus/spi/devices/spi0.0/setup',0x62)
    jogio.deviceWrite('/sys/bus/spi/devices/spi0.0/averaging',0x3c)
    jogio.deviceWrite('/sys/bus/spi/devices/spi0.0/conversion',0xb9)
    v=[]
    v.append(jogio.deviceRead('/sys/bus/spi/devices/spi0.0/in6_input'))
    v.append(jogio.deviceRead('/sys/bus/spi/devices/spi0.0/in4_input'))
    v.append(jogio.deviceRead('/sys/bus/spi/devices/spi0.0/in5_input'))
    v.append(jogio.deviceRead('/sys/bus/spi/devices/spi0.0/in2_input'))
    return v

def infraredSingle(side):
    """
    Get reflectance value (expressed in mV) on a given infrared sensors
    side defines which sensor is used
    side == "front" : front infrared
    side == "left": left infrared
    side == "right" : right infrared
    side == "rear" : rear infrared
    """
    jogio.deviceWrite('/sys/bus/spi/devices/spi0.0/setup',0x62)
    jogio.deviceWrite('/sys/bus/spi/devices/spi0.0/averaging',0x3c)
    jogio.deviceWrite('/sys/bus/spi/devices/spi0.0/conversion',0xb9)
    if (side == "front"):
        v = jogio.deviceRead('/sys/bus/spi/devices/spi0.0/in6_input')
    elif (side == "left"):
        v = jogio.deviceRead('/sys/bus/spi/devices/spi0.0/in4_input')
    elif (side == "right"):
        v = jogio.deviceRead('/sys/bus/spi/devices/spi0.0/in5_input')
    elif (side == "rear"):
        v = jogio.deviceRead('/sys/bus/spi/devices/spi0.0/in2_input')
    else:
        v = 0
    return v

# temperature in ADC chip
def temperatureAdc():
    """ 
    return the temperature (in degrees) measure by ADC chip
    """
    v = jogio.deviceRead ('/sys/bus/spi/devices/spi0.0/temp1_input')
    return float(v)/1000.0

# adcPrintStatus , showimg content of setup, averaging and conversion registers
def adcPrintStatus():
    """
    display values in ADC registers (for debug purpose)
    """
    print "ADC Status -------------------------------------------"
    setup = jogio.deviceRead('/sys/bus/spi/devices/spi0.0/setup')
    conversion = jogio.deviceRead('/sys/bus/spi/devices/spi0.0/conversion')
    averaging = jogio.deviceRead('/sys/bus/spi/devices/spi0.0/averaging')
    print "ADC Setup register : %3d (0x%2.2x)"%(setup,setup)
    print "ADC Conversion register : %3d (0x%2.2x)"%(conversion,conversion)
    print "ADC Averaging register : %3d (0x%2.2x)"%(averaging,averaging)
    print "------------------------------------------------------"
#
# unitary tests of JOG's sensors and actuators

if __name__ == "__main__":

    # leds
    ledsSet (9)
    print "leds : %x"%(ledsGet())
    time.sleep(1)
    ledsSet (6)
    print "leds : %x"%(ledsGet())
    time.sleep(1)
    ledsSet (0)
    print "leds : %x"%(ledsGet())

    # compass
    print "Compass LR : %6.1f"%(compassLowRes())
    print "Compass HR : %6.1f"%(compassHighRes())
    time.sleep(2)

    # sonars
    allson=sonarAll()
    print "All sonars : %5.1f %5.1f %5.1f %5.1f %5.1f"%(allson[0],allson[1],
                                                        allson[2],allson[3],
                                                        allson[4])
    print "Sonar Left      : %5.1f"%(sonarSingle(1))
    print "Sonar Mid Left  : %5.1f"%(sonarSingle(2))
    print "Sonar Center    : %5.1f"%(sonarSingle(3))
    print "Sonar Mid Right : %5.1f"%(sonarSingle(4))
    print "Sonar Right     : %5.1f"%(sonarSingle(5))
    time.sleep(1)



    # infrareds and temperature
    jogio.deviceInit()  # init ADC (load driver module and setup)

    infrall = infraredAll()
    print "ADC chip Temperature : %f"%(temperatureAdc())
    print "Infrareds : ",infrall
    time.sleep(0.2)
    print "Infrared Front : %4d "%(infraredSingle('front'))
    time.sleep(0.2)
    print "Infrared Left  : %4d "%(infraredSingle('left'))
    time.sleep(0.2)
    print "Infrared Right : %4d "%(infraredSingle('right'))
    time.sleep(0.2)
    print "Infrared Rear  : %4d "%(infraredSingle('rear'))
    time.sleep(0.2)
    adcPrintStatus()

    print "Sonar Center    : %5.1f"%(sonarSingle(3))
    for i in range(15):
        print "Sonar Center    : %5.1f"%(sonarSingle(3))
        ledsSet (i+1)
        time.sleep(4)

    jogio.fullStop()
