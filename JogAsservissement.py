__author__ = 'Fenix'

import numpy as np


class Jog():

    def __init__(self, x, y, theta):
        self.state = np.array([x, y, theta])
        self.target = np.array([0, 0, 0])
        self.allies = []

    def update_closest_allies(self, v1, v2):
        self.allies = [np.array(v1), np.array(v2)]

    def asservissement(self):
        #TODO
        print self.allies
        pass