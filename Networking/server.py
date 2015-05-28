# -*- coding: utf-8 -*-

import socket, math

# demarrage du serveur
server = 		"127.0.0.1"
port = 			55042
mysock = 		socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mysock.bind((server, port))

INTERCEPTION_RANGE = 	2.
MISSION_FINISHED =	False

JOG_IP = 		[None]*10
JOG_coordinates= 	[None]*10
ennemy_coordinates = 	[0.0,0.0]
ennemy_velocity = 	[0.0,0.0]

# ne peut être appelée qu'à condition que tous les tableaux soient remplis
def update_coordinates() :
	global JOG_IP, JOG_coordinates, ennemy_coordinates
	for e in JOG_IP :
		# détermination des deux plus proches voisins
		JOG_ID = 		JOG_IP.index(e)
		current_coordinates = 	JOG_coordinates[JOG_ID]
		distances = 		[float("inf")]*10
		for c in JOG_coordinates :
			if c != current_coordinates :
				distances[JOG_coordinates.index(c)] = math.sqrt( (c[0]-current_coordinates[0])**2 + (c[1]-current_coordinates[1])**2  )

		neighbour1_ID = distances.index(min(distances))
		distances[distances.index(min(distances))] = max(distances)
		neighbour2_ID = distances.index(min(distances))
		
		# formatage et envoi du message
		msg_coordinates = 'C'+' '+'A'+str(JOG_coordinates[neighbour1_ID][0])+' '+'A'+str(JOG_coordinates[neighbour1_ID][1])+' '+'B'+str(JOG_coordinates[neighbour2_ID][0])+' '+'B'+str(JOG_coordinates[neighbour1_ID][1])+' '+'T'+str(ennemy_coordinates[0])+'T'+str(ennemy_coordinates[1])+' '+'T'+str(ennemy_velocity[1])+'V'+str(ennemy_velocity[1])
		mysock.sendto(msg_coordinates, e)

while True :
	msg, client = mysock.recvfrom(255)
	if MISSION_FINISHED :
		for e in JOG_IP :
			mysock.sendto('F',e)
	if msg & not(MISSION_FINISHED) :
		msg_parts = msg.split()
		JOG_IP[msg_parts[0]] = client
		if msg_parts[1] == 'C' :	# cas où le message reçu est une mise à jour de la position
			JOG_X = 			float(msg_parts[2])
			JOG_Y = 			float(msg_parts[3])
			JOG_coordinates[msg_parts[0]] =	[JOG_X, JOG_Y]
			# vérification de la distance à l'ennemi
			if ( math.sqrt( (JOG_X-ennemy_coordinates[0])**2 + (JOG_Y-ennemy_coordinates[1])**2 ) <= INTERCEPTION_RANGE ) :
				MISSION_FINISHED = True
		elif msg_parts[1] == 'E' :	# cas où le message reçu est une erreur
			# TODO
			pass
		if not( (None in JOG_IP) | (None in JOG_coordinates) ) :
			update_coordinates()
