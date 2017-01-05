#!/usr/bin/python3
from socket import *
from sys import *
from grid import *
from random import *



def init():
	global me
	me = socket(AF_INET6,SOCK_STREAM,0)
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

def main():
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
							main()
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
								main()
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
					main()
				else:
					quit(0)
			elif data == b'l':
				print("Loser.")
				if input("Voulez-vous rejouer? [O/N]").lower() == 'o':
					relog()
					main()
				else:
					quit(0)
			elif data == b'd':
				print("Match nul !")
				if input("Voulez-vous rejouer? [O/N]").lower() == 'o':
					relog()
					main()
				else:
					quit(0)
		except (EOFError):
			print("Non, là, il fallait entrer soit O, soit N. Pas EOF.")
			me.close()
			quit(0)
	else:
		quit(0)



if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("\nSale lâcheur.")
		quit(0)
