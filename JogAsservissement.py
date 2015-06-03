# coding=utf-8
__author__ = 'Fenix'

import threading
import numpy as np
from numpy.linalg import norm
from Jog_Utils.jog_highlevel import *
from Jog_Utils.jogio import *
from Jog_Utils.jogio_cmd_motors import *
from math import atan2


# Frame : +Y is North, +X is East.
class Jog():
    MAX_WHEEL_SPEED = 0.6  # m/s
    SAFETY_MARGIN = 2  # m
    TICKS_PER_TURN = 576
    WHEEL_DIAMETER = 0.058928
    WHEEL_E = 0.2
    TICKS_TO_METER = WHEEL_DIAMETER * pi / TICKS_PER_TURN
    NORMAL_SPEED = 0.4  # m/s
    KP_ORI = MAX_WHEEL_SPEED / pi
    KD_ORI = 2
    KI_ORI = 0.05
    KP_SPEED = 50
    KI_SPEED = 30

    def __init__(self, x, y, user, dt):
        self.position = np.array([x, y])
        self.theta = get_theta()
        self.target = None
        self.target_max_known_speed = 0
        self.motor_speeds = np.array([0.0, 0.0])
        self.id = user
        self.odos = np.array(get_odometry())
        self.allies = []
        self.dt = dt
        self.commands = [0, 0]
        self.I_error_speed = np.array([0.0, 0.0])
        self.I_error_theta = 0
        self.motor_curr_direction = [1, 1]
        self.motor_curr_direction_order = [1, 1]
        p = open("logasserv.txt", "w")
        p.write("")
        p.close()
        p = open("log_theta.txt", "w")
        p.write("")
        p.close()

    def update_closest_allies(self, v1, v2):
        self.allies = [np.array(v1), np.array(v2)]

    def update_target(self, v):  # Contains x,y,vx,vy
        self.target = np.array(v)

    def asservissement(self):
        t = threading.Timer(self.dt, self.asservissement)
        t.daemon = True
        t.start()
        initime = time.clock()  # Comment after debugging
        last_theta = self.theta
        # Update state
        self.update_state()
        self.asserv_speed(self.order(last_theta))
        # self.asserv_speed(self.test_order())
        print "Asservissement routine executed in ", time.clock() - initime, "s"  # Comment after debugging

    def test_order(self):
        return np.array([-Jog.NORMAL_SPEED, -Jog.NORMAL_SPEED])

    def order(self, last_theta):
        p = np.array([0, 0])
        if self.target is not None:
            # Détermination de la direction à prendre
            targ_dir = self.test_dir()
            #targ_dir = self.determine_dir()
            with open("log_theta.txt", "a") as logfile:
                logfile.write(" ".join([str(time.time()), str(atan2(targ_dir[1], targ_dir[0])), str(self.theta)]))
                logfile.write("\n")
            # targ_dir = self.determine_dir()  # décommenter si non test.
            targ_dir_ori = atan2(targ_dir[1], targ_dir[0])
            delta_ori = ((targ_dir_ori - self.theta + pi) % (2 * pi)) - pi
            self.I_error_theta += delta_ori
            d_theta = self.theta - last_theta
            if abs(delta_ori) > pi / 6:  # Requiert de tourner avant de commencer à avancer
                print "REQUEST TURN"
                p = [ Jog.NORMAL_SPEED * (Jog.KP_ORI*delta_ori - Jog.KD_ORI*d_theta),
                     -Jog.NORMAL_SPEED * (Jog.KP_ORI*delta_ori + Jog.KD_ORI*d_theta)]
            else:  # Assez bien orienté vers la destination pour aller "droit"
                print "REQUEST CURVEMOVE"
                p = [Jog.NORMAL_SPEED * (1 + Jog.KP_ORI*delta_ori - Jog.KD_ORI*d_theta + Jog.KI_ORI*self.I_error_theta),
                     Jog.NORMAL_SPEED * (1 - Jog.KP_ORI*delta_ori + Jog.KD_ORI*d_theta - Jog.KI_ORI*self.I_error_theta)]
        else:
            p = np.array([0, 0])
        return p

    def asserv_speed(self, targ_speed):
        self.I_error_speed += targ_speed - self.motor_speeds
        self.commands[0] = min(100, max(-100, self.commands[0] + Jog.KP_SPEED * (
            targ_speed[0] - self.motor_speeds[0]) + Jog.KI_SPEED * self.I_error_speed[0]))
        self.commands[1] = min(100, max(-100, self.commands[1] + Jog.KP_SPEED * (
            targ_speed[1] - self.motor_speeds[1]) + Jog.KI_SPEED * self.I_error_speed[1]))
        with open("logasserv.txt", "a") as logfile:
            logfile.write(" ".join([str(time.time()),
                                    str(targ_speed[0]), str(self.motor_speeds[0]),
                                    str(targ_speed[1]), str(self.motor_speeds[1]),
                                    str(self.I_error_speed[0]), str(targ_speed[0] - self.motor_speeds[0]),
                                    str(self.commands[0]), str(self.commands[1])]))
            logfile.write("\n")
        motors_set_direction(self.commands[0], self.commands[1])
        self.motor_curr_direction_order = [copysign(1, self.commands[0]), copysign(1, self.commands[1])]
        motors_set_speed(abs(self.commands[0]), abs(self.commands[1]))

    def vect_to_target(self, position):
        return self.target[2:] - position

    def update_state(self):
        new_odos = np.array(get_odometry())
        wheels_speed = Jog.TICKS_TO_METER * (new_odos - self.odos) / self.dt
        theta = get_theta()
        wheels_speed = self.compute_wheel_direction_state_based(wheels_speed)
        speed = np.mean(wheels_speed)
        self.position += speed * np.array([np.cos(theta), np.sin(theta)])
        self.motor_speeds = wheels_speed
        self.odos = new_odos
        self.theta = theta

    # Method working. May need some refinement.
    def compute_wheel_direction_state_based(self, wheels_speed):
        dv = wheels_speed - self.motor_speeds
        for i in [0, 1]:
            if self.motor_curr_direction[i] != self.motor_curr_direction_order[i] and dv[i] > 0:
                self.motor_curr_direction[i] = -self.motor_curr_direction[i]
        return np.array(
            [wheels_speed[0] * self.motor_curr_direction[0], wheels_speed[1] * self.motor_curr_direction[1]])

    # Method leading to numerous mistakes on too many cases. Could be refined.
    # Not meant to be used in its current state.
    def compute_wheel_direction_compass_based(self, wheels_speed, theta):
        dtheta = (theta - self.theta) / self.dt
        possible_dtheta = [self.dtheta(wheels_speed[0], wheels_speed[1]),
                           self.dtheta(-wheels_speed[0], wheels_speed[1]),
                           self.dtheta(wheels_speed[0], -wheels_speed[1]),
                           self.dtheta(-wheels_speed[0], -wheels_speed[1])]
        min_delta = 10000
        k = 0
        for i in range(4):
            delta = abs(possible_dtheta[i] - dtheta)
            if delta < min_delta:
                k = i
                min_delta = delta
        if (k % 2) == 1:
            wheels_speed[0] = - wheels_speed[0]
            print "LEFT WHEEL BACKWARD"
        else:
            print "LEFT WHEEL FRONTWARD"
        if k > 1:
            wheels_speed[1] = - wheels_speed[1]
            print "RIGHT WHEEL BACKWARD"
        else:
            print "RIGHT WHEEL FRONTWARD"
        return wheels_speed


    def determine_dir(self):
        v2center = self.vect_to_target(self.position)
        d2center = norm(v2center)
        ennemy_velocity = 1.3 * norm(self.target[2:])  # Permet d'anticiper jusqu'à 30% de la vitesse max adverse connue
        self.target_max_known_speed = max(self.target_max_known_speed, ennemy_velocity)
        intercept_range_self = d2center * Jog.MAX_WHEEL_SPEED / self.target_max_known_speed

        v2prerob = self.allies[0] - self.position
        d2prerob = norm(v2prerob)
        intercept_range_pre = d2prerob * Jog.MAX_WHEEL_SPEED / self.target_max_known_speed

        v2postrob = self.allies[1] - self.position
        d2postrob = norm(v2postrob)
        intercept_range_post = d2postrob * Jog.MAX_WHEEL_SPEED / self.target_max_known_speed

        p = d2prerob - intercept_range_pre - intercept_range_self
        q = d2postrob - intercept_range_post - intercept_range_self

        targ_dir = np.array([0, 0])
        # algorithmes de regulation des intercepteurs autour de l'ennemi
        if (p < -Jog.SAFETY_MARGIN) and (q < -Jog.SAFETY_MARGIN):
            targ_dir = v2center / d2center
        elif p <= q and ((q > - Jog.SAFETY_MARGIN) != (p > -Jog.SAFETY_MARGIN)):
            targ_dir = v2postrob / d2postrob
        elif p > q and ((q > - Jog.SAFETY_MARGIN) != (p > -Jog.SAFETY_MARGIN)):
            targ_dir = v2prerob / d2prerob
        else:
            if norm(self.vect_to_target(self.allies[1])) > d2center:
                targ_dir = v2postrob / d2postrob
            if norm(self.vect_to_target(self.allies[0])) < d2center:
                targ_dir = v2prerob / d2prerob
        return targ_dir

    def test_dir(self):
        return np.array([0, 1])

    def dtheta(self, v1, v2):
        return (v2 - v1) / Jog.WHEEL_E