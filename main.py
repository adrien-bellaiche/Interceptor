# coding=utf-8
__author__ = 'Fenix'
from JogAsservissement import Jog
from Jog_Utils.jogio import *
from Utils import *
import socket

ERROR_ALLGOOD = 0
ERROR_STUCK = 1
ERROR_MSG_FAILED = 2

DT = 0.2

x, y, selfid, serverIP, serverPort = parse_mission_file('mission.conf')
robot = Jog(x, y, selfid, DT)
mysock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
started = False

#msgin, rserver = mysock.recvfrom(255)


def main():
    device_init()
    robot.asservissement()
    while not started:
        retrieve_data()
    while started:
        retrieve_data()


def retrieve_data():
    global started
    msgin, rserver = mysock.recvfrom(255)
    if len(msgin) == 0:
        report_error(ERROR_MSG_FAILED)
        return
    msg = msgin.split(" ")
    if msg[0] == "C":
        if len(msg) != 9:
            report_error(ERROR_MSG_FAILED)
            return
        ally1 = [0, 0]
        ally2 = [0, 0]
        target = [0, 0, 0, 0]
        e_codes = [1 for _ in range(8)]
        if msg[1][0] != 'A':
            e_codes[0], ally1[0] = parse_position(msg[1])
        if msg[2][0] != 'A' and e_codes[0] == 0:
            e_codes[1], ally1[1] = parse_position(msg[2])
        if msg[3][0] != 'B':
            e_codes[2], ally2[0] = parse_position(msg[3])
        if msg[4][0] != 'B' and e_codes[2] == 0:
            e_codes[3], ally2[1] = parse_position(msg[4])
        robot.update_closest_allies(ally1, ally2)

        if msg[5][0] != 'T':
            e_codes[4], target[0] = parse_position(msg[5])
        if msg[6][0] != 'T' and e_codes[4] == 0:
            e_codes[5], target[1] = parse_position(msg[6])
        if msg[7][0] != 'V' and e_codes[5] == 0:
            e_codes[6], target[2] = parse_position(msg[7])
        if msg[8][0] != 'V' and e_codes[6] == 0:
            e_codes[7], target[3] = parse_position(msg[8])
        if e_codes[6] == 0:
            robot.update_target(target)
    elif msg[0] == "S":
        started = True
    elif msg[0] == "F":
        started = False


def send_coords():
    msg = [robot.id, 'C', robot.position[0], robot.position[1]]
    mysock.sendto(" ".join(msg), (serverIP, serverPort))


def report_error(errorid):
    mysock.sendto(" ".join(['E', errorid]), (serverIP, serverPort))

if __name__ == "__main__":
    main()