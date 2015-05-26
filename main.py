# coding=utf-8
__author__ = 'Fenix'
from twisted.internet import task
from twisted.internet import reactor
from JogAsservissement import Jog

robot = Jog('mission.conf')
asservissement = task.LoopingCall(robot.asservissement)


def main():
    asservissement.start(0.3)  # call every 0.3s
    # l.stop() will stop the looping calls
    reactor.run()
    while is_viable():
        if not is_connected():
            reconnect()
        if is_connected():
            retrieve_data()


def is_viable():
    pass


def is_connected():
    pass


def retrieve_data():
    # Selon les ordres :
    # arrêt mission : asservissement.stop()
    # positions :
    pass


def reconnect():
    pass


if __name__ == "__main__":
    main()