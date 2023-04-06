from .chess_constants import *
from .board_class import *
import discord

class Chess:
    def __init__(self):
        self._init()
    
    def draw(self):
        board_message = self.board.draw()
        return board_message
    def update(self):
        self.possible_moves = 0
        self.player_check = False
        self.computer_check = False
        #self.board.check_if_promotion(self.turn)
    def _init(self):
        self.selected = None 
        self.board = Board()
        self.turn = 0
        self.valid_moves = []
        self.attacked_squares= []
        self.board.get_all_valid_moves(0)
        self.start_embed = discord.Embed(title="Test")
    
    def reset(self):
        self._init()
    
    def select(self,row,col):
        if self.selected:
            result = self._move(row,col)
            if not result:
                self.selected = None 
                self.select(row,col)
        if self.board.player_promotion:
            if self.cpu != None:
                if self.board.promotion_piece.color == self.cpu.color:
                    self.promotion = None
                    return False
            pawn = self.board.promotion_piece
            promotion_piece = None
            if pawn.color == 0:
                promotion_rows = [1,2,3,4]
                opp_color = 1
            else:
                promotion_rows = [6,5,4,3]
                opp_color = 0
            if row == promotion_rows[0]:
                self.board.create_piece(PieceTypes.Bishop,pawn)
                promotion_piece = self.board.get_piece(pawn.row,pawn.col)
                self.turn = opp_color
            elif row == promotion_rows[1]:
                self.board.create_piece(PieceTypes.Knight,pawn)
                promotion_piece = self.board.get_piece(pawn.row,pawn.col)
                self.board.player_promotion = False
                self.turn = opp_color
            elif row == promotion_rows[2]:
                self.board.create_piece(PieceTypes.Rook,pawn)
                promotion_piece = self.board.get_piece(pawn.row,pawn.col)
                self.turn = opp_color
            elif row == promotion_rows[3]:
                self.board.create_piece(PieceTypes.Queen,pawn)
                promotion_piece = self.board.get_piece(pawn.row,pawn.col)
                self.turn = opp_color
            if promotion_piece != None and promotion_piece != 0:
                self.board.player_promotion = False
                self.board.append_piece(promotion_piece)
                self.board.remove_piece(pawn)
                self.board.get_all_valid_moves(self.turn)
                self.update()
            return 
        piece = self.board.get_piece(row,col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece 
            self.valid_moves = self.board.get_valid_moves(piece,False)
            return True
            
        return False
      

    def _move(self,row,col):
        piece = self.board.get_piece(row,col)
        if self.selected  and (row,col) in self.valid_moves:
            if piece != 0:
                if piece.color != self.turn:
                    self.board.remove(piece)
                    self.board.move_piece(self.selected, row, col)
                    #self.change_turn()
            else:
                self.board.move_piece(self.selected, row, col)
            self.change_turn()
        else:
            return False
        
        return True
    def change_turn(self):
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
                self.computer_check = self.board.check
            else:
                self.board.check_if_check(0)
                self.turn = 0
                self.player_check = self.board.check
