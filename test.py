# coding=utf-8
__author__ = 'Fenix'


from JogAsservissement import *
from Utils import *
from Jog_Utils.jogio import *

if __name__ == "__main__":
    device_init()
    #setHeadingSimple(10)
    DT = 0.1
    x, y, selfid, serverIP, serverPort = parse_mission_file('mission.conf')
    robot = Jog(x, y, selfid, DT)
    robot.update_target([0.5, 0.5, 0, 0])
    robot.asservissement()
    time.sleep(100)
