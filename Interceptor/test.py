# coding=utf-8
__author__ = 'Fenix'

from JogCommand.jogio import device_init
import time


if __name__ == "__main__":
    device_init()
    time.sleep(2)
    #setHeadingSimple(10)
    DT = 0.2
    from JogCommand.JogAsservissement import *
    from JogCommand.Utils import *
    x, y, selfid, serverIP, serverPort = parse_mission_file('mission.conf')
    robot = Jog(x, y, selfid, DT)
    robot.set_command_mode(Jog.COMMAND_UNDEFINED)
    robot.target = [0.5, 0.5]
    robot.start()
    time.sleep(100)
