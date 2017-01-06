#!/usr/bin/python3
from grid import *
from socket import *
import select


host = socket(AF_INET,SOCK_STREAM,0)
client_select = [] 
client_socket = []

#init
def host_start():
	host.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	try:
		host.bind((gethostbyname(gethostname()),4402))
		print("Servers up at ( hostname = " + gethostname()+ " )"+gethostbyname(gethostname()) + ".\n You can connect using either of those as argument for the client.")
	except gaierror:
		host.bind(('',4402))
		print("Servers up, listening on all interfaces.\n Please ask clients connect to your machine's IP/hostname.\n Local testing can be done using ./client.py ''.")
	host.listen(1)
	client_select.append(host)

#identify a client
#@id : index 
def client_getinfo(id):
	return client_socket[id-1]


#adds a player
#@player_s : socket
def add_player(player_s):
	#Check if there isn't a leaver in a room
	for i in range(len(client_socket)):
		if client_socket[i] == 'Q':
			client_socket[i] = player_s
			return 0
	client_socket.append(player_s)


#Deletes an user
#@player_s : socket 
def delete_user(player_s):
	index = client_select.index(player_s)
	i = client_socket.index(player_s)
	client_socket[i] = 'Q'
	client_select.pop(index)


#Sends user info to advance game
#@index : users' index in client_socket
#@data : data to be sent
def status(data,index):
	client_getinfo(index).send(data.encode())

#Creates a game (waits for connection)
def waiter():
	user, adress = host.accept()
	client_select.append(user)
	add_player(user)

def reset():
	del client_select[:]
	del client_socket[:]
	client_select.append(host)

def main():
	grids = [grid(), grid(), grid()]
	current_player = J1
	current,_,_ = select.select(client_select,[],[])
	while len(client_socket) < 2:
		for user in current:
			if user == host:
				waiter()
	while True :
		status('y',current_player)
		shot = -1
		current,_,_ = select.select(client_select,[],[])
		for user in current:
			if user == host:
				waiter()
			else:
				if user == client_getinfo(current_player):
					data = user.recv(64)
					if not data:
						user.close()
						delete_user(user)
					elif data in [b'0',b'1',b'2',b'3',b'4',b'5',b'6',b'7',b'8']:
						shot = int(data)
						print(str(current_player) + " plays at " + str(shot))
						break #We got our shot, let's place it
				else:
				#If it's not the host or the current player, maybe we got a leaver
				#Check it out
					data = user.recv(1024)
					if not data:
						user.close()
						delete_user(user) 
						continue
		try:
			if grids[0].gameOver() == -1:
				if (grids[0].cells[shot] != EMPTY):
					grids[current_player].cells[shot] = grids[0].cells[shot]
					status(str(grids[current_player].cells[shot]),current_player)
				else:
					grids[current_player].cells[shot] = current_player
					grids[0].play(current_player, shot)
					status(str(grids[current_player].cells[shot]),current_player)
					current_player = current_player%2+1
		except AssertionError:
			try:
				status('d',J1)
				data = client_getinfo(J1).recv(1)
				if data == b'y':
					print("J1 decided to stay connected while J2 quitted during match.\nWaiting for another player...")
				reset()
				main()
			except (ConnectionResetError,AttributeError):
				status('d',J2)
				data = client_getinfo(J2).recv(1)
				if data == b'y':
					print("J2 decided to stay connected while J1 quitted during match.\nWaiting for another player...")
				reset()
				main()
		if grids[0].gameOver() != -1:
			status('e',J1)
			status('e',J2)
			grids[0].display()
			if grids[0].gameOver() == J1:
				status('w',J1)
				status('l',J2)
			elif grids[0].gameOver() == J2:
				status('w',J2)
				status('l',J1)
			else:
				status('d',J2)
				status('d',J1)
			print("Game ended. Prompting clients for a rematch or waiting for another player and restarting...")
			dataJ1 = client_getinfo(J1).recv(1)
			dataJ2 = client_getinfo(J2).recv(1)
			if dataJ1 == b'y' and dataJ2 == b'y':
				reset()
				main()
			elif dataJ1 == b'y':
				#status('o',J1)
				print("J2 left. looking for another player...")
				reset()
				main()
			elif dataJ2 == b'y':
				#status('o',J2)
				print("J1 left. looking for another player...")
				reset()
				main()
			else:
				reset()
				print("All players left. Restarting room.")
				main()
		

if __name__ == "__main__":
	host_start()
	try:
		main()
	except KeyboardInterrupt:
		reset()
		print("\n Server got Ctrl+C'd by it's meanie administrator.")
		host.close()
		quit(0)