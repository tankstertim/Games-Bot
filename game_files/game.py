from other_files.constants import X, O, EMPTY_SQUARE
from .TicTacToe import TicTacToe
from .HangMan import HangMan
from .connect4 import Connect4
from other_files.enums import GameTypes
from chess_files.game import *
class Game:
  def __init__(self, p1, p2, guild, computer,game_type,channel,p1_prob= None,p2_prob = None):
    self.p1 = p1
    self.p2 = p2
    self.a_prob =p1_prob
    self.b_prob = p2_prob
    self.turn = p1
    self.winner = None
    self.guild = guild
    self.channel = channel
    self.message = None
    self.user_error_message = None
    self.game_type = game_type
    if game_type == 1:
      self.game = TicTacToe(p1,p2,computer,channel)
      self.game_choice = GameTypes.ttt.value
    if game_type == 2:
      self.game = HangMan(p1,p2,channel)
      self.game_choice = GameTypes.hm.value
    if game_type == 3:
      self.game = Connect4(p1,p2)
      self.game_choice = GameTypes.c4.value
    if game_type == 4:
      self.game = Chess()
      self.game_choice = GameTypes.chess.value
    self.invite_accepted = False
    
    

  def draw(self):
    board_message = self.game.draw()
    return board_message
