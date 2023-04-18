from .chess_constants import * 
from other_files.enums import PieceTypes
class Piece:
    def __init__(self,row,col,color):
        self.row = row 
        self.col = col 
        self.color = color
        self.moves = 0
        self.prev_move = None
        self.attacked_squares = []
        self.valid_moves = []
        self.key = None
    
    def get_position(self):
        return [self.row,self.col]
    
    def get_valid_moves(self, piece):
        pass
    def move(self,piece, new_row, new_col):
        piece.moves += 1
        if piece.type == PieceTypes.Pawn:
            piece.previous_move_amnt = abs(piece.row-new_row)
            if self.moves >= 1:
                self.first_move = False
        piece.row = new_row
        piece.col = new_col
        return
    
    def get_moves(self):
        if self.type == PieceTypes.Pawn:
            if self.first_move:
                return 2, 0, 0
            return 1, 0, 0
        if self.type == PieceTypes.Knight:
            return 0, 0 ,0
        if self.type == PieceTypes.Bishop:
            return 0, 0 , 8 
        if self.type == PieceTypes.Rook:
            return 8,8, 0
        if self.type == PieceTypes.Queen:
            return  8, 8 , 8
        if self.type == PieceTypes.King:
            return 1, 1, 1
    

    


class Pawn(Piece):
    def __init__(self, row,col,color):
        super().__init__(row,col,color)
        self.first_move =  True
        self.second_move = False
        self.previous_move_amnt = 0
        self.moved_two_spaces = False
        self.price = 100
        self.key = None
        self.in_passing_turns = 0
        self.can_in_pass = False
        self.take_pawn = False
        self.stayed_moves = 0
        self.take_piece = []
        self.take_pos = {}
        self.type = PieceTypes.Pawn
        if self.color == 0:
            self.image = WHITE_PAWN_IMAGE
        else:
            self.image = BLACK_PAWN_IMAGE

    
    def check_in_passing(self,board):
        if 0 <= self.col+1 <= 7:
            attacking_piece = board[self.row][self.col+1]
            if attacking_piece != 0:
                if self.moves == 1 and attacking_piece.type == PieceTypes.Pawn and attacking_piece.color != self.color:
                    if self.previous_move_amnt == 2 and self.in_passing_turns == 0:
                       
                       self.can_in_pass = True
                       self.in_passing_turns += 1
                       return True
                  
                                 
        if 0 <= self.col-1 <= 7:
            attacking_piece =board[self.row][self.col-1]
            if attacking_piece != 0:
                if self.moves == 1 and attacking_piece.type == PieceTypes.Pawn and attacking_piece.color != self.color:
                    if self.previous_move_amnt == 2 and self.in_passing_turns == 0:
                        self.can_in_pass = True
                        self.in_passing_turns += 1
                        return True
          
        self.can_in_pass = False
        self.in_passing_turns += 1
        return False
                
                    


class Knight(Piece):
    def __init__(self, row,col, color):
        super().__init__(row,col,color)
        self.price = 300
        self.type = PieceTypes.Knight
        if self.color == 0:
            self.image = WHITE_KNIGHT_IMAGE
        else:
            self.image = BLACK_KNIGHT_IMAGE


class Bishop(Piece):
    def __init__(self, row,col, color):
        super().__init__(row,col,color)
        self.price = 300
        self.type = PieceTypes.Bishop
        if self.color == 0:
            self.image = WHITE_BISHOP_IMAGE
        else:
            self.image = BLACK_BISHOP_IMAGE
        


class Queen(Piece):
    def __init__(self, row,col,color):
        super().__init__(row,col,color)
        self.price = 900
        self.type = PieceTypes.Queen
        if self.color == 0:
            self.image = WHITE_QUEEN_IMAGE
        else:
            self.image = BLACK_QUEEN_IMAGE
        

class King(Piece):
    def __init__(self, row,col,color):
        super().__init__(row,col,color)
        self.type = PieceTypes.King
        self.first_move = True
        self.castle = False
        self.rook_pos = []
        self.castled_rook = None
        self.castle_pos = []
        self.castled = False
        self.castled_pos = None
        if self.color == 0:
            self.image = WHITE_KING_IMAGE
        else:
            self.image = BLACK_KING_IMAGE
        
        
class Rook(Piece):
    def __init__(self, row,col,color):
        super().__init__(row,col,color)
        self.type = PieceTypes.Rook
        self.price = 500
        self.check = False
        self.first_move = True
        if self.color == 0:
            self.image = WHITE_ROOK_IMAGE
        else:
            self.image = BLACK_ROOK_IMAGE