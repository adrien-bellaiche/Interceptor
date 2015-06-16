#-*-coding:utf-8-*-
import socket

import pygame
from pygame.locals import *


J_AXIS_WE =		0
J_AXIS_NS =		1
J_INTERVAL_W =		[-2.0, -0.5]
J_INTERVAL_E =		[+0.1, +2.0]
J_INTERVAL_0WE =	[-0.3, +0.1]
J_INTERVAL_N =		[-2.0, -0.5]
J_INTERVAL_S =		[+0.5, +2.0]
J_INTERVAL_0NS =	[-0.3, +0.3]
joystick_WE =		0
joystick_NS =		0

server = 		"172.20.12.63"
port = 			55142
mysock = 		socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mysock.bind((server, port))

def initialisation():
	global client
	msg, client = mysock.recvfrom(255)
	pygame.init()
	fenetre = pygame.display.set_mode((640, 480))
	nb = pygame.joystick.get_count()
	print str(nb) + " joystick(s) detectes"
	if(nb > 0):
		print "Activation du 1er joystick"
		mon_joystick = pygame.joystick.Joystick(0)
		mon_joystick.init()
		return True
	return False


def action_joystick_axe(axe, valeur):
	global joystick_WE, joystick_NS, client
	if	axe == J_AXIS_WE:
		if	J_INTERVAL_W[0] <= valeur <= J_INTERVAL_W[1]:
			joystick_WE = -1
		elif	J_INTERVAL_E[0] <= valeur <= J_INTERVAL_E[1]:
			joystick_WE = 1
		elif	J_INTERVAL_0WE[0] <= valeur <= J_INTERVAL_0WE[1]:
			joystick_WE = 0
	if	axe == J_AXIS_NS:
		if J_INTERVAL_N[0] <= valeur <= J_INTERVAL_N[1]:
			joystick_NS = -1
		elif	J_INTERVAL_S[0] <= valeur <= J_INTERVAL_S[1]:
			joystick_NS = 1
		elif	J_INTERVAL_0NS[0] <= valeur <= J_INTERVAL_0NS[1]:
			joystick_NS = 0
	print str(joystick_WE)+','+str(joystick_NS)+'\n'
	mysock.sendto('CONS'+str(joystick_WE)+','+str(joystick_NS), client)


def bouclage():
	while True :
		for event in pygame.event.get():
			if	event.type == QUIT:
				continuer = False
			elif	event.type == JOYAXISMOTION:
				action_joystick_axe(event.axis, event.value)
		continue;

if __name__ == "__main__":
	initialisation()
	bouclage()
