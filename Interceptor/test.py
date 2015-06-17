# coding=utf-8
__author__ = 'Fenix'

if __name__ == "__main__":
    device_init()
    time.sleep(2)
    #setHeadingSimple(10)
    DT = 0.2
    from JogCommand.JogAsservissement import *
    from JogCommand.Utils import *
    x, y, selfid, serverIP, serverPort = parse_mission_file('mission.conf')
    robot = Jog(x, y, selfid, DT)
    robot.update_target([0.5, 0.5, 0, 0])
    robot.start()
    time.sleep(100)
