from .tictactoe_computer import computer_move
from other_files.constants import *
import discord

class TicTacToe:

  def __init__(self,p1,p2,computer, channel):
    self.board = [[EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE] for i in range(3)]
    self.p1 = p1
    self.p2 = p2
    self.turn = p1
    self.winner = None
    self.computer = computer
    self.channel = channel
    self.start_embed = discord.Embed(title = 'TicTacToe Commands')
    self.start_embed.add_field(name = '!place', value = 'Type in !place (pos) to mark.')
    self.start_embed.add_field(name = '/quit', value = 'Type in /quit to leave the game.', inline = False)
  
  def check_win(self):
    print("Board:", self.board)
    for i in range(len(self.board)):
      if self.board[i][0] == self.board[i][1] == self.board[i][2] and self.board[i][0] != EMPTY_SQUARE:
        self.winner =self.turn
        return True
      if self.board[0][i] == self.board[1][i] == self.board[2][i] and self.board[0][i] != EMPTY_SQUARE:
        self.winner = self.turn
        return True
    if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] != EMPTY_SQUARE:
      self.winner = self.turn
      return True
    if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] != EMPTY_SQUARE:
      self.winner = self.turn
      return True
    openSpots = 0
    for i in range(len(self.board)):
      for j in range(len(self.board)):
        if self.board[i][j] == EMPTY_SQUARE:
          openSpots += 1
    if openSpots == 0:
      self.winner = 'tie'
      return True
    return False
  
  def move(self, pos):
    if pos % 3 == 0:
      pos_y = (pos // 3) - 1
    else:
      pos_y = pos // 3
    pos_x = (pos - (3 * (pos // 3))) - 1
    if self.board[pos_y][pos_x] != EMPTY_SQUARE:
      return False
    if self.turn == self.p1:
      self.board[pos_y][pos_x] = X
    elif self.turn == self.p2:
      self.board[pos_y][pos_x] = O
    self.change_turn()
    return True
  
  def change_turn(self):
    self.check_win()
    print(self.board)
    print("winner2: ", self.winner)
    print("turn:", self.turn)

    if self.winner == None and self.computer:
      self.turn = self.p2
      move = computer_move(self.board, O, X, 9)
      self.board[move[0]][move[1]] = O
      self.check_win()
      self.turn = self.p1
      return
    if self.turn == self.p1:
      self.turn = self.p2
    else:
      self.turn = self.p1

  def draw(self):
    board_string = ''
    for i in range(len(self.board)):
      for j in range(len(self.board)):
        board_string += self.board[i][j]
      board_string += '\n'
    return board_string 