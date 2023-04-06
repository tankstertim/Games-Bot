from enum import Enum


#bot enums
class GameTypes(Enum):
  hm = 'hangman'
  ttt = 'tictactoe'
  c4 = 'connect4'
  chess = 'chess'

class GameMode(Enum):
  vote = 1
  chaos = 2
class GameNames(Enum):
  hangman = "Hangman"
  tictactoe =  "Tic Tac Toe"
  connect4 = "Connect 4"

#chess enums
class MoveAxis(Enum):
    X = 'x'
    Y = 'y'
    D = 'd'

class PieceTypes(Enum):
    Pawn = 1
    Knight = 2
    Bishop = 3
    Rook = 4
    Queen = 5
    King = 6