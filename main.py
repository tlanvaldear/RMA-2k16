#!/usr/bin/python3

from grid import *
import  random
from sys import *
import socket
import select

def main():
    if len(argv) == 1:
        #Create host sockets and gameconfig
        s = socket.socket(socket.AF_INET6,socket.SOCK_STREAM,0)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        slist = []
        s.bind(('',7777))
        s.listen(1)
        while True:
            important, idc, idk = select.select(slist + [s], [], [])
            for so in important : 
                if so == s:
                    sock, addr = s.accept()
                    slist += [sock]
                    ip = addr[0]
                    bip = bytearray(ip,'UTF-8')
                    for sockt in slist:
                        sockt.send(b"A NEW PLAYER JOINED: " + bip + b"\n")
                else:
                    byt = so.recv(2048)
                    if not byt: 
                        so.close()
                        slist.remove(so)
                        for sockt in slist:
                            sockt.send(b"LEAVE: " + b"\n")
                    else:
                        print(byt)
            if len(slist) == -1:
                continue #Do nothing, there's only the server !
            else:
                if (len(slist)) % 2 == 0: #We got a game !
                    grids = [grid(), grid(), grid()]
                    current_player = J1
                    grids[J1].display()
                    while grids[0].gameOver() == -1:
                        if current_player == J1:
                            shot = -1
                            while shot <0 or shot >=NB_CELLS:
                                shot = int(input ("Quelle case allez-vous jouer ?")) #Excepts when user inputs EOF or alpha chars
                        else:
                            shot = random.randint(0,8)
                            while grids[current_player].cells[shot] != EMPTY:
                                shot = random.randint(0,8)
                        if (grids[0].cells[shot] != EMPTY):
                            grids[current_player].cells[shot] = grids[0].cells[shot]
                        else:
                            grids[current_player].cells[shot] = current_player
                            grids[0].play(current_player, shot)
                            current_player = current_player%2+1
                        if current_player == J1:
                            grids[J1].display()
                    print("game over")
                    grids[0].display()
                    if grids[0].gameOver() == J1:
                        print("You win !")
                    else:
                        print("You lose !")
                        break
    else:
        #Connect to host sockets and get gameconfig
        #Redef J1&J2 via those sockets
        player = socket.socket(socket.AF_INET6,socket.SOCK_STREAM,0)
        player.connect(("",7777))

main()