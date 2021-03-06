import socket
from JogCommand.jogio import device_init
import time

def go_go(gadgeto_jog):
    while True:
        mysock.sendto(msgout, (server, port))
        msgin, rserver = mysock.recvfrom(255)
        msg = msgin[4::].split(',')
        if msg[0] == "0":
            if msg[1] == "1":
                gadgeto_jog.target = [- Jog.NORMAL_SPEED, 0]
            elif msg[1] == "-1":
                gadgeto_jog.target = [Jog.NORMAL_SPEED, 0]
            elif msg[1] == "0":
                gadgeto_jog.target = [0, 0]
        elif msg[0] == "1":
            if msg[1] == "0":
                gadgeto_jog.target = [Jog.NORMAL_SPEED, 90]
            elif msg[1] == "1":
                gadgeto_jog.target = [Jog.NORMAL_SPEED, 135]
            elif msg[1] == "-1":
                gadgeto_jog.target = [Jog.NORMAL_SPEED, 45]
        elif msg[0] == "-1":
            if msg[1] == "0":
                gadgeto_jog.target = [Jog.NORMAL_SPEED, -90]
            elif msg[1] == "1":
                gadgeto_jog.target = [Jog.NORMAL_SPEED, -135]
            elif msg[1] == "-1":
                gadgeto_jog.target = [Jog.NORMAL_SPEED, -45]


if __name__ == "__main__":
    mysock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = "127.0.0.1"  # Pour test sur Vjog
    # server = "172.20.12.63"
    port = 55142
    msgout = "CLIENT DISPONIBLE"

    device_init()
    time.sleep(2)
    DT = 0.2
    from JogCommand.JogAsservissement import *

    robot = Jog(0, 0, 0, DT)
    robot.set_command_mode(Jog.COMMAND_MANUAL)
    robot.target = [0, 0]  # [speed, orientation (repere du robot)]
    robot.start()
    go_go(robot)