#!/usr/bin/python3
from socket import *
from sys import *
from grid import *

grid = grid()
me = socket(AF_INET6,SOCK_STREAM,0)
def me_player():
	me.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	me.connect((argv[1],4402))
def relog():
	#TODO
def main():
	game = True
	while game == True:
		fiyerd = False
		data = me.recv(1)
		if len(data) == 1:
			if data == b'y':
				fiyerd = True
			else:
				game = False #Because it ended, get out of the loop
		if fiyerd:
			grid.display()
			me_attack = -1
			while int(me_attack) < 0 or int(me_attack) > NB_CELLS:
				me_attack = input("Quelle case allez-vous jouer ? (entrez un chiffre entre 0 et 8)\n>")
			me.send(me_attack.encode())
			ans = me.recv(1)
			if ans in [b'1',b'2']:
				grid.cells[int(me_attack)] = int(ans)
			else:
				game = False #Issues happened, the game closed.
	data = me.recv(1)
	if data == b'w':
		print("You won!")
		#prompt for rematch
		#wip
		if input("Voulez-vous rejouer? [O/N]").lower() == 'o':
			relog()
			main()
	elif data == b'l':
		print("Loser.")
		if input("Voulez-vous rejouer? [O/N]").lower() == 'o':
			relog()
			main()
	elif data == b'd':
		print("Match nul !")
		if input("Voulez-vous rejouer? [O/N]").lower() == 'o':
			relog()
			main()



if __name__ == '__main__':
	me_player()
	main()