import socket, time

mysock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mysock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mysock3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mysock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mysock5 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server = "127.0.0.1"
port = 55042

msgout1 = "0 C 21.42 84.24"
msgout2 = "1 C 23.42 84.24"
msgout3 = "2 C 25.42 84.24"
msgout4 = "3 C 27.42 84.24"
msgout5 = "4 C 29.42 84.24"
while True :
	mysock1.sendto(msgout1, (server, port))
	mysock2.sendto(msgout2, (server, port))
	mysock3.sendto(msgout3, (server, port))
	mysock4.sendto(msgout4, (server, port))
	mysock5.sendto(msgout5, (server, port))
	time.sleep(3)
	msgin1, rserver = mysock1.recvfrom(255)
	msgin2, rserver = mysock2.recvfrom(255)
	msgin3, rserver = mysock3.recvfrom(255)
	msgin4, rserver = mysock4.recvfrom(255)
	msgin5, rserver = mysock5.recvfrom(255)
	print msgin1 + '\n' + msgin2 + '\n' + msgin3 + '\n' + msgin4 + '\n' + msgin5 + '\n'
