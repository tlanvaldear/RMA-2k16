# RMA-2k16
Blind Tic-Tac-Toe university project using TCP/IP

## Principle
### V1.
Player A starts the game and faces an AI in a local game. 
Player A doesn't see the AI (Player B) moves unless he tries to do a move on somewhere the AI has already played. If so, this specific move is unveiled on Player A's board.

### V2.
Two players face each other
Player A doesn't see what Player B does and so on.

The game ends when either :
> One of the players completed a line without being interrupted by the other (horizontal, diagonal, vertical)

> The board is filled up (Draw)

# How To Use
Execute`./main.py` to play Version 1.
## V2.
Execute `./host.py` to start hosting in localhost.

Execute two instances of `./client.py` that connect to `''` , meaning `localhost` in order to start a game
