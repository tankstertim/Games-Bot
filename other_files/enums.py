from enum import Enum

class GameTypes(Enum):
  hm = 'hangman'
  ttt = 'tictactoe'
  c4 = 'connect4'

class GameMode(Enum):
  vote = 1
  chaos = 2
class GameNames(Enum):
  hangman = "Hangman"
  tictactoe =  "Tic Tac Toe"
  connect4 = "Connect 4"