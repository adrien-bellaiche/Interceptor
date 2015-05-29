import socket

mysock =	socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server =	"127.0.0.1"
port =		55142
msgout =	"CLIENT DISPONIBLE"

while True :
	mysock.sendto(msgout, (server, port))
	msgin, rserver = mysock.recvfrom(255)
	print msgin
