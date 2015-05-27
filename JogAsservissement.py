__author__ = 'Fenix'

import numpy as np
from Jog_Utils.jog_highlevel import *


# Frame : +Y is North, +X is East.
class Jog():
    def __init__(self, x, y, user):
        self.state = np.array([x, y, get_theta()])
        self.target = np.array([0, 0, 0])
        self.id = user
        self.allies = []

    def update_closest_allies(self, v1, v2):
        self.allies = [np.array(v1), np.array(v2)]

    def update_target(self, v):  # Contains x,y,vx,vy
        self.target = np.array(v)

    def asservissement(self):
        #TODO
        pass