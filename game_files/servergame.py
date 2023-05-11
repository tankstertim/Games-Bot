from other_files.constants import X, O, EMPTY_SQUARE
from .TicTacToe import TicTacToe
from .HangMan import HangMan
from .connect4 import Connect4
from chess_files.game import Chess
from other_files.enums import GameTypes

class ServerGame():
  def __init__(self,guild1,guild2,game_type,mode, target_channel,current_channel):
    self.guild1 = guild1
    self.guild2 = guild2
    self.current_channel = current_channel
    self.target_channel = target_channel
    self.a_prob = 0
    self.b_prob = 0
    self.winner = None
    self.current_messages = {}
    self.turn = self.guild1
    self.mode = mode
    self.invite_accepted = False
    if game_type == 1:
      self.game = TicTacToe(self.guild1,self.guild2,False,current_channel)
      self.game_choice = GameTypes.ttt.value
    elif game_type == 2:
      self.game =HangMan(self.guild1,self.guild2,current_channel)
      self.game_choice = GameTypes.hm.value
    elif game_type == 3:
      self.game =Connect4(self.guild1,self.guild2)
      self.game_choice = GameTypes.c4.value
    elif game_type == 4:
      self.game =Chess(self.guild1,self.guild2)
      self.game_choice = GameTypes.chess.value
  def draw(self):
    if self.game_choice == GameTypes.chess.value:
      self.turn = self.game.player_turn
    elif self.game_choice != GameTypes.hm.value:
      self.turn = self.game.turn
    board_message = self.game.draw()
    self.winner= self.game.winner
    return board_message