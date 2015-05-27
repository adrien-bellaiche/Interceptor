"""
module jogio_cmd_motors : controlling motors via FPGA registers
"""

from Jog_Utils.jogio import fpga_read, fpga_write

motorDirectionForward = 0x0
motorDirectionBackward = 0x1
motorPeriodRegister = 0x0006
motorStopAllRegister = 0x0004
motorPwmSpeedLeftRegister = 0x0008
motorPwmDirectionLeftRegister = 0x000A
motorPwmSpeedRightRegister = 0x000C
motorPwmDirectionRightRegister = 0x000E


def motor_init():
    """
    init both motors (forward, speed=0)
    """
    fpga_write(motorStopAllRegister, 0)
    fpga_write(motorPeriodRegister, 100)
    fpga_write(motorPwmSpeedLeftRegister, 0)
    fpga_write(motorPwmDirectionLeftRegister, motorDirectionForward)
    fpga_write(motorPwmSpeedRightRegister, 0)
    fpga_write(motorPwmDirectionRightRegister, motorDirectionForward)


def stop_all():
    """
    stop both motors (speed=0)
    """
    fpga_write(motorStopAllRegister, 0)


def motor_set_period(p):
    """
    set PWM period
    if period=100, PWM speed can go from 0 (stop) to 99 (full speed)
    """
    fpga_write(motorPeriodRegister, p)


def motor_display_status():
    """
    display motors status
    """
    print "------------------------------------------"
    print "Left  motor direction is ", fpga_read(motorPwmDirectionLeftRegister)
    print "Left  motor speed is     ", fpga_read(motorPwmSpeedLeftRegister)
    print "Right motor direction is ", fpga_read(motorPwmDirectionRightRegister)
    print "Right motor speed is     ", fpga_read(motorPwmSpeedRightRegister)
    print "------------------------------------------"


def motor_left_forward():
    """
    set motor left forwards 
    warning : left speed is set to 0 before changing direction
    """
    d = fpga_read(motorPwmDirectionLeftRegister)
    if d != motorDirectionForward:
        fpga_write(motorPwmSpeedLeftRegister, 0)
        fpga_write(motorPwmDirectionLeftRegister, motorDirectionForward)


def motor_right_forward():
    """
    set motor right forwards
    warning : right speed is set to 0 before changing direction
    """
    d = fpga_read(motorPwmDirectionRightRegister)
    if d != motorDirectionForward:
        fpga_write(motorPwmSpeedRightRegister, 0)
        fpga_write(motorPwmDirectionRightRegister, motorDirectionForward)


def motor_left_backward():
    """
    set motor left backwards
    warning : left speed is set to 0 before changing direction
    """
    d = fpga_read(motorPwmDirectionLeftRegister)
    if d == motorDirectionForward:
        fpga_write(motorPwmSpeedLeftRegister, 0)
        fpga_write(motorPwmDirectionLeftRegister, motorDirectionBackward)


def motor_right_backward():
    """
    set motor right backwards
    warning : right speed is set to 0 before changing direction
    """
    d = fpga_read(motorPwmDirectionRightRegister)
    if d == motorDirectionForward:
        fpga_write(motorPwmSpeedRightRegister, 0)
        fpga_write(motorPwmDirectionRightRegister, motorDirectionBackward)


def motor_left_set_speed(s):
    """
    set motor left speed (PWM duty cycle)
    """
    if s < 0:
        s = 0
    smx = fpga_read(motorPeriodRegister) - 1
    # print "smx=",smx,", s=",s
    if s > smx:
        s = smx
    fpga_write(motorPwmSpeedLeftRegister, s)


def motor_right_set_speed(s):
    """
    set motor right speed (PWM duty cycle) 
    """
    if s < 0:
        s = 0
    smx = fpga_read(motorPeriodRegister) - 1
    # print "smx=",smx,", s=",s
    if s > smx:
        s = smx
    fpga_write(motorPwmSpeedRightRegister, s)


def motors_set_speed(s_left, s_right):
    """
    set speed for both motors :
    sLeft : speed of letf motor
    sRight : speed of right motor
    """
    motor_left_set_speed(s_left)
    motor_right_set_speed(s_right)


def motors_set_direction(dir_left, dir_right):
    """
    set direction for both motors :
    dirLeft : if >= 0 forwards, if < 0 backwards
    dirRight : if >= 0 forwards, if < 0 backwards
    """
    if dir_left < 0:
        motor_left_backward()
    else:
        motor_left_forward()
    if dir_right < 0:
        motor_right_backward()
    else:
        motor_right_forward()