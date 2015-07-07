# coding=utf-8
__author__ = 'Fenix'

import threading
from math import atan2, cos, sin

from jog_highlevel import *
from jogio_cmd_motors import *
from Utils import norm, list_dif, list_mul, list_add


# Frame : +Y is East, +X is North.
class Jog(object):
    COMMAND_UNDEFINED = -1
    COMMAND_DIRECTION = 0
    COMMAND_TARGET = 1
    COMMAND_MANUAL = 2
    COMMAND_WAYPOINT = 3
    MAX_WHEEL_SPEED = 0.4  # m/s
    SAFETY_MARGIN = 2  # m
    TICKS_PER_TURN = 576
    WHEEL_DIAMETER = 0.058928
    WHEEL_E = 0.2
    TICKS_TO_METER = WHEEL_DIAMETER * pi / TICKS_PER_TURN
    NORMAL_SPEED = 0.3  # m/s
    THRESH_ORI = pi/4
    ROTATION_SPEED_CAP = 2  # rad/s. Plus d'un demi tour par seconde.
    ROTATION_WHEEL_SPEED = ROTATION_SPEED_CAP*WHEEL_E/2
    KP_ORI = 1/THRESH_ORI
    KD_ORI = - 2*KP_ORI
    KI_ORI = KP_ORI / 40
    KP_SPEED = 20
    KD_SPEED = - 20
    KI_SPEED = 90

    def __init__(self, x, y, user, dt):
        self.target_reset = False
        motor_init()
        self.position = [x, y]
        self.theta = get_theta()
        self._target = None
        self.target_max_known_speed = 0
        self.motor_speeds = [0.0, 0.0]
        self.id = user
        self.odos = get_odometry()
        self.allies = []
        self.dt = dt
        self.command_type = Jog.COMMAND_UNDEFINED
        self.commands = [0, 0]
        self.I_error_speed = [0.0, 0.0]
        self.I_error_ori = 0.0
        self.D_speed = [0.0, 0.0]
        self.motor_curr_direction = [1, 1]
        self.motor_curr_direction_order = [1, 1]
        self.init_logs()
        self.started = False
        self.skipped = 0

    def start(self):
        self.started = True
        self.asservissement()

    def init_logs(self):
        self.init_log("logodometry.txt")
        self.init_log("logasserv.txt")
        self.init_log("logtheta.txt")
        self.init_log("logpos.txt")

    @staticmethod
    def init_log(filename):
        p = open(filename, "w")
        p.write("")
        p.close()

    def update_closest_allies(self, v1, v2):
        self.allies = [v1, v2]

    def asservissement(self):
        if self.started:
            t = threading.Timer(self.dt, self.asservissement)
            t.daemon = True
            t.start()
        last_theta = self.theta
        # Update state
        if self.update_state() == 0:
            #self.asserv_speed(self.test_order())
            self.asserv_speed(self.order(last_theta))

    def set_command_mode(self, mode):
        self.command_type = mode
        self.target_reset = True

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, p):
        """
        :param p:   COMMAND_UNDEFINED : Par défaut. Permet de tester les asservissements.
                    COMMAND_DIRECTION : target = [vitesse, angle_dans_le_repère_global]
                    COMMAND_TARGET : Méthode d'interception en meute. target = [X,Y,VX,VY], repère global.
                    COMMAND_MANUAL : Idéal pour un target = [vitesse, angle_dans_le_repère_robot]
                    COMMAND_WAYPOINT : target = [X,Y] repère global
        :return: None
        """
        if self.command_type == Jog.COMMAND_MANUAL:
            self._target = [p[0], (p[1] * pi / 180 + self.theta) % (2 * pi)]  # Correspond à [V, theta] repère global
        else:
            self._target = p
        self.target_reset = False

    @staticmethod
    def test_order():
        return [Jog.NORMAL_SPEED, Jog.NORMAL_SPEED]

    def manual_dir(self):
        return self.target

    def order(self, last_theta):
        if self._target is not None:
            # Détermination de la direction à prendre
            targ = None
            if self.command_type == Jog.COMMAND_DIRECTION:
                # TODO les self.dir doivent cracher v,theta, et pas la direction uniquement.
                pass
            elif self.command_type == Jog.COMMAND_TARGET:
                targ = self.determine_dir()
            elif self.command_type == Jog.COMMAND_MANUAL:
                targ = self.manual_dir()
            elif self.command_type == Jog.COMMAND_UNDEFINED:
                targ = self.test_dir()
            elif self.command_type == Jog.COMMAND_WAYPOINT:
                # TODO les self.dir doivent cracher v,theta, et pas la direction uniquement.
                pass
            with open("logtheta.txt", "a") as logfile:
                logfile.write(" ".join([str(time.time()), str(targ[1]), str(self.theta)]))
                logfile.write("\n")
            delta_ori = ((targ[1] - self.theta + pi) % (2 * pi)) - pi
            d_theta = ((self.theta - last_theta + pi) % (2 * pi)) - pi
            if targ[0] != 0:
                if abs(delta_ori) > Jog.THRESH_ORI:  # Besoin de tourner pour s'aligner à peu près
                    vi = copysign(Jog.ROTATION_WHEEL_SPEED, delta_ori)
                    return [vi, -vi]
                else:
                    dv = abs(targ[0]) * (Jog.KP_ORI * delta_ori + Jog.KD_ORI * d_theta)
                    return [targ[0] + dv, targ[0] - dv]
            else:
                return [0, 0]
        else:
            return [0, 0]

    def asserv_speed(self, targ_speed):
        self.I_error_speed = list_add(list_dif(targ_speed, self.motor_speeds), self.I_error_speed)
        new_left = min(100, max(-100,
                                Jog.KP_SPEED * (targ_speed[0] - self.motor_speeds[0])
                                + Jog.KD_SPEED * self.D_speed[0]
                                + Jog.KI_SPEED * self.I_error_speed[0]))
        new_right = min(100, max(-100,
                                 Jog.KP_SPEED * (targ_speed[1] - self.motor_speeds[1])
                                 + Jog.KD_SPEED * self.D_speed[1]
                                 + Jog.KI_SPEED * self.I_error_speed[1]))
        self.commands[0] = min(new_left, self.commands[0] + 15)
        self.commands[1] = min(new_right, self.commands[1] + 15)
        with open("logasserv.txt", "a") as logfile:
            logfile.write(" ".join([str(time.time()),
                                    str(targ_speed[0]), str(self.motor_speeds[0]),
                                    str(targ_speed[1]), str(self.motor_speeds[1]),
                                    str(self.I_error_speed[0]), str(targ_speed[0] - self.motor_speeds[0]),
                                    str(self.commands[0]), str(self.commands[1])]))
            logfile.write("\n")
        motors_set_direction(self.commands[0], self.commands[1])
        self.motor_curr_direction_order = [copysign(1, self.commands[0]), copysign(1, self.commands[1])]
        motors_set_speed(int(abs(self.commands[0])), int(abs(self.commands[1])))

    def vect_to_target(self, position):
        return self._target[0:2] - position

    def update_state(self):
        new_odos = get_odometry()
        wheels_speed = list_mul(Jog.TICKS_TO_METER / self.dt / (self.skipped + 1), list_dif(new_odos, self.odos))
        with open("logodometry.txt", "a") as logfile:
            logfile.write(" ".join([str(new_odos[0]), str(new_odos[1])]))
            logfile.write("\n")
        if wheels_speed[0] < 0 or wheels_speed[1] < 0:
            self.skipped += 1
            return -1
        theta = get_theta()
        wheels_speed = self.compute_wheel_direction_state_based(wheels_speed)
        speed = 0.5 * (wheels_speed[0] + wheels_speed[1])
        self.position += [speed * cos(theta), speed * sin(theta)]
        self.D_speed = list_dif(wheels_speed, self.motor_speeds)
        self.motor_speeds = wheels_speed
        self.odos = new_odos
        self.theta = theta
        with open("logpos.txt", "a") as logfile:
            logfile.write(" ".join([str(self.position[0]), str(self.position[1])]))
            logfile.write("\n")
        if self.skipped > 0:
            self.skipped = 0
        return 0

    # Method working. May need some refinement.
    def compute_wheel_direction_state_based(self, wheels_speed):
        dv = list_dif(wheels_speed, self.motor_speeds)
        for i in [0, 1]:
            if self.motor_curr_direction[i] != self.motor_curr_direction_order[i] and dv[i] > 0:
                self.motor_curr_direction[i] = -self.motor_curr_direction[i]
        return [wheels_speed[0] * self.motor_curr_direction[0], wheels_speed[1] * self.motor_curr_direction[1]]

    def determine_dir(self):
        v2center = self.vect_to_target(self.position)
        d2center = norm(v2center)
        ennemy_velocity = 1.3 * norm(
            self._target[2:])  # Permet d'anticiper jusqu'à 30% de la vitesse max adverse connue
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

        targ_dir = [0, 0]
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
        return [Jog.NORMAL_SPEED, atan2(targ_dir[1], targ_dir[0])]

    @staticmethod
    def test_dir():
        return [- 0.3, 0]

    @staticmethod
    def dtheta(v1, v2):
        return (v2 - v1) / Jog.WHEEL_E