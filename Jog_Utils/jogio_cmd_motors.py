"""
module jogio_cmd_motors : controlling motors via FPGA registers
"""

from Jog_Utils.jogio import fpgaRead, fpgaWrite

motorDirectionForward = 0x0
motorDirectionBackward = 0x1
motorPeriodRegister = 0x0006
motorStopAllRegister = 0x0004
motorPwmSpeedLeftRegister = 0x0008
motorPwmDirectionLeftRegister = 0x000A
motorPwmSpeedRightRegister = 0x000C
motorPwmDirectionRightRegister = 0x000E


def motorInit():
    """
    init both motors (forward, speed=0)
    """
    fpgaWrite(motorStopAllRegister, 0)
    fpgaWrite(motorPeriodRegister, 100)
    fpgaWrite(motorPwmSpeedLeftRegister, 0)
    fpgaWrite(motorPwmDirectionLeftRegister, motorDirectionForward)
    fpgaWrite(motorPwmSpeedRightRegister, 0)
    fpgaWrite(motorPwmDirectionRightRegister, motorDirectionForward)


def stopAll():
    """
    stop both motors (speed=0)
    """
    fpgaWrite(motorStopAllRegister, 0)


def motorSetPeriod(p):
    """
    set PWM period
    if period=100, PWM speed can go from 0 (stop) to 99 (full speed)
    """
    fpgaWrite(motorPeriodRegister, p)


def motorDisplayStatus():
    """
    display motors status
    """
    print "------------------------------------------"
    print "Left  motor direction is ", fpgaRead(motorPwmDirectionLeftRegister)
    print "Left  motor speed is     ", fpgaRead(motorPwmSpeedLeftRegister)
    print "Right motor direction is ", fpgaRead(motorPwmDirectionRightRegister)
    print "Right motor speed is     ", fpgaRead(motorPwmSpeedRightRegister)
    print "------------------------------------------"


def motorLeftForward():
    """
    set motor left forwards 
    warning : left speed is set to 0 before changing direction
    """
    d = fpgaRead(motorPwmDirectionLeftRegister)
    if d != motorDirectionForward:
        fpgaWrite(motorPwmSpeedLeftRegister, 0)
        fpgaWrite(motorPwmDirectionLeftRegister, motorDirectionForward)


def motorRightForward():
    """
    set motor right forwards
    warning : right speed is set to 0 before changing direction
    """
    d = fpgaRead(motorPwmDirectionRightRegister)
    if d != motorDirectionForward:
        fpgaWrite(motorPwmSpeedRightRegister, 0)
        fpgaWrite(motorPwmDirectionRightRegister, motorDirectionForward)


def motorLeftBackward():
    """
    set motor left backwards
    warning : left speed is set to 0 before changing direction
    """
    d = fpgaRead(motorPwmDirectionLeftRegister)
    if d == motorDirectionForward:
        fpgaWrite(motorPwmSpeedLeftRegister, 0)
        fpgaWrite(motorPwmDirectionLeftRegister, motorDirectionBackward)


def motorRightBackward():
    """
    set motor right backwards
    warning : right speed is set to 0 before changing direction
    """
    d = fpgaRead(motorPwmDirectionRightRegister)
    if d == motorDirectionForward:
        fpgaWrite(motorPwmSpeedRightRegister, 0)
        fpgaWrite(motorPwmDirectionRightRegister, motorDirectionBackward)


def motorLeftSetSpeed(s):
    """
    set motor left speed (PWM duty cycle)
    """
    if s < 0:
        s = 0
    smx = fpgaRead(motorPeriodRegister) - 1
    # print "smx=",smx,", s=",s
    if s > smx:
        s = smx
    fpgaWrite(motorPwmSpeedLeftRegister, s)


def motorRightSetSpeed(s):
    """
    set motor right speed (PWM duty cycle) 
    """
    if s < 0:
        s = 0
    smx = fpgaRead(motorPeriodRegister) - 1
    # print "smx=",smx,", s=",s
    if s > smx:
        s = smx
    fpgaWrite(motorPwmSpeedRightRegister, s)


def motorsSetSpeed(s_left, s_right):
    """
    set speed for both motors :
    sLeft : speed of letf motor
    sRight : speed of right motor
    """
    motorLeftSetSpeed(s_left)
    motorRightSetSpeed(s_right)


def motorsSetDirection(dir_left, dir_right):
    """
    set direction for both motors :
    dirLeft : if >= 0 forwards, if < 0 backwards
    dirRight : if >= 0 forwards, if < 0 backwards
    """
    if dir_left < 0:
        motorLeftBackward()
    else:
        motorLeftForward()
    if dir_right < 0:
        motorRightBackward()
    else:
        motorRightForward()

