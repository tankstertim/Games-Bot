from .chess_constants import *
from .board_class import *
import discord

class Chess:
    def __init__(self,p1,p2):
        self._init(p1,p2)
    
    def draw(self):
        board_message = self.board.draw()
        return board_message
    def update(self):
        self.movesible_moves = 0
        self.player_check = False
        self.computer_check = False
        #self.board.check_if_promotion(self.turn)
    def _init(self,p1,p2):
        self.col_dict = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H":7}
        self.selected = None 
        self.board = Board()
        self.turn = 0
        self.player_turn = p1
        self.p1 = p1
        self.p2 = p2
        self.winner = None
        self.valid_moves = []
        self.attacked_squares= []
        self.board.get_all_valid_moves(0)
        self.start_embed = discord.Embed(title="Test")
    
    def reset(self):
        self._init()
    def move(self,pos):
        move = pos.upper()
        if len(move) != 4:
            return False
        if (ord(move[0]) < 65 or ord(move[0]) > 72) or (ord(move[2]) < 65 or ord(move[2]) > 72):
            return False
        if (int(move[1]) < 1 or int(move[1]) > 8) or (int(move[3]) < 1 or int(move[3]) > 8):
            return False
        curr_row = 8+int(move[1])*-1
        curr_col =int(self.col_dict[move[0]])
        target_row = 8+int(move[3])*-1
        target_col = int(self.col_dict[move[2]])
        curr_piece = self.board.get_piece(curr_row,curr_col)
        if curr_piece ==0:
          return False
        if curr_piece.color != self.turn:
          return False
        target_piece = self.board.get_piece(target_row,target_col)
        valid_moves = self.board.get_valid_moves(curr_piece,False)
        print(curr_row,curr_col)
        print(target_row,target_col)
        if not (target_row,target_col) in valid_moves:
            return False
        if target_piece != 0:
            if target_piece.color != self.turn:
                self.board.remove(target_piece)
                self.board.move_piece(curr_piece, target_row, target_col)
                #self.change_turn()
        else:
            self.board.move_piece(curr_piece, target_row, target_col)
        self.change_turn()
        print('done')
        return True

    
    def change_turn(self):
        self.update()
        self.valid_moves = []
        self.board.check = False
        #self.attacked_squares = self.board.get_attacked_pieces(self.turn)
        self.board.check_if_promotion(self.turn)
        self.board.update_pawn_pass()

        self.selected = None
        if not self.board.player_promotion:
            if self.turn == 0:
                self.board.check_if_check(1)
                self.turn = 1
                self.player_turn = self.p2
                self.computer_check = self.board.check
            else:
                self.board.check_if_check(0)
                self.turn = 0
                self.player_turn = self.p1
                self.player_check = self.board.check
        self.board.get_all_valid_moves(self.turn)
        if self.board.checkmate:
            if self.turn == 0:
                self.winner = self.p2
            else:
                self.winner = self.p1
