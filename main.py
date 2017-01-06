#!/usr/bin/python3
from grid import *
from socket import *
import select
from sys import *
from random import *


############CLIENT#######################
def init():
	global me
	me = socket(AF_INET,SOCK_STREAM,0)
	global grille
	grille = grid()

def me_player():
	global me
	init()
	me.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	me.connect((argv[1],4402))


def relog():
	me.send('y'.encode())
	me.close()
	return 0

def vs_ia():
	grids = [grid(), grid(), grid()]
	current_player = J1
	grids[J1].display()
	while grids[0].gameOver() == -1:
		if current_player == J1:
			shot = -1
			while shot <0 or shot >=NB_CELLS:
				try:
					shot = int(input ("Quelle case allez-vous jouer ? (entrez un chiffre entre 0 et 8)\n>"))
				except (EOFError, ValueError):
					print("Veuillez entrer un entier de 0 à 8.")
		else:
			shot = randint(0,8)
			while grids[current_player].cells[shot] != EMPTY:
				shot = randint(0,8)
		if (grids[0].cells[shot] != EMPTY):
			grids[current_player].cells[shot] = grids[0].cells[shot]
		else:
			grids[current_player].cells[shot] = current_player
			grids[0].play(current_player, shot)
			current_player = current_player%2+1
		if current_player == J1:
			grids[J1].display()
	grids[0].display()
	if grids[0].gameOver() == J1:
		print("You win !")
	elif grids[0].gameOver() == J2:
		print("Loser.")
	else:
		print("Match nul !")

def client():
	if input("Voulez-vous jouer contre l'IA ? [O/N]").lower() == 'o':
		vsia = True
		vs_ia()
		while vsia == True:
			if input("Voulez-vous rejouer une partie contre l'IA ? [O/N]").lower() == 'o':
				vs_ia()
			else:
				vsia = False
	else:
		if input("Voulez-vous jouer en réseau ? [O/N]").lower() != 'o':
			quit(0)
		else:
			reseau = True
	if reseau == True or input("Voulez-vous jouer en réseau ? [O/N]").lower() == 'o':
		init()
		me_player()
		game = True
		while game == True:
			fiyerd = False
			data = me.recv(1)
			if len(data) == 1:
				if data == b'y':
					fiyerd = True
				elif data == b'd':
					print("L'adversaire a abandonné.")
					try:
						if input("Voulez-vous rejouer? [O/N]").lower() == 'o':
							relog()
							client()
						else:
							quit(0)
					except (EOFError):
						print("Non, là, il fallait entrer soit O, soit N. Pas faire le malin avec son Ctrl+D.")
						me.close()
						quit(0)
				else:
					game = False #Because it ended, get out of the loop
			if fiyerd:
				grille.display()
				me_attack = -1
				egg = 0
				while me_attack < 0 or me_attack > NB_CELLS:
					try:
						me_attack = int(input("Quelle case allez-vous jouer ? (entrez un chiffre entre 0 et 8)\n>"))
					except (EOFError, ValueError):
						egg += 1
						if egg == 3:
							print ("Ok, ok. J'ai compris, on va faire autrement. Je vais donc faire ton tour à ta place...")
							me_attack = randint(0,8)
						else:
							print("Veuillez entrer un entier, de préférence entre 0 et 8.")
							me_attack = -1
				me.send(str(me_attack).encode())
				ans = me.recv(1)
				if ans in [b'1',b'2']:
					grille.cells[int(me_attack)] = int(ans)
				else:
					game = False #Issues happened, the game closed.
					if ans == b'd':
						print("L'adversaire a abandonné.")
						try:
							if input("Voulez-vous rejouer? [O/N]").lower() == 'o':
								relog()
								client()
							else:
								quit(0)
						except (EOFError):
							print("Non, là, il fallait entrer soit O, soit N. Pas faire le malin avec son Ctrl+D.")
							me.close()
							quit(0)
		data = me.recv(1)
		try:
			if data == b'w':
				print("You won!")
				#prompt for rematch
				#wip
				if input("Voulez-vous rejouer? [O/N]").lower() == 'o':
					relog()
					client()
				else:
					quit(0)
			elif data == b'l':
				print("Loser.")
				if input("Voulez-vous rejouer? [O/N]").lower() == 'o':
					relog()
					client()
				else:
					quit(0)
			elif data == b'd':
				print("Match nul !")
				if input("Voulez-vous rejouer? [O/N]").lower() == 'o':
					relog()
					client()
				else:
					quit(0)
		except (EOFError):
			print("Non, là, il fallait entrer soit O, soit N. Pas EOF.")
			me.close()
			quit(0)
	else:
		quit(0)

##############SERVER####################
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

def host_main():
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
				host_main()
			except (ConnectionResetError,AttributeError):
				try:
					status('d',J2)
					data = client_getinfo(J2).recv(1)
					if data == b'y':
						print("J2 decided to stay connected while J1 quitted during match.\nWaiting for another player...")
					reset()
					host_main()
				except (ConnectionResetError,AttributeError):
					reset()
					host_main()
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
				host_main()
			elif dataJ1 == b'y':
				#status('o',J1)
				print("J2 left. looking for another player...")
				reset()
				host_main()
			elif dataJ2 == b'y':
				#status('o',J2)
				print("J1 left. looking for another player...")
				reset()
				host_main()
			else:
				reset()
				print("All players left. Restarting room.")
				host_main()
		

if __name__ == "__main__":
	if len(argv) < 2:
		host_start()
		try:
			host_main()
		except KeyboardInterrupt:
			reset()
			print("\n Server got Ctrl+C'd by it's meanie administrator.")
			host.close()
			quit(0)
	else:
		try:
			client()
		except KeyboardInterrupt:
			print("\nSale lâcheur.")
			quit(0)