import discord
from .chess_constants import *
from .pieces import *
from other_files.enums import *
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
class Board:
    def __init__(self):
        self.board = [[0 for j in range(8)] for i in range(8)]
        self.pieces = []
        self.check = False
        self.player_promotion = False
        self.computer_check = False
        self.player_check = False
        self.promotion_piece = None
        self.promotion_pawn = None
        self.kings = []
        self.player_checkmate = False
        self.computer_checkmate = False
        self.player_color = 0
        self.computer_promotion = False
        self.computer_color = None
        self.checkmate = False
        self.checkmate_color = None
        self.pawns_pass= []
        self.king_attacked_squares = []
        self.white_board_pieces = []
        self.black_board_pieces = []
        for i in range(8):
            for j in range(8):
                self.king_attacked_squares.append((i,j))
        self.white_pieces_left = 16
        self.black_pieces_left = 16
        self.create_board_pieces()
        self.get_black_and_white_pieces()
        return 
    
    def draw(self):
        chess_board = Image.new("RGBA",(WIDTH,HEIGHT), DARK_SQUARE)
        font = ImageFont.truetype(BOARD_FONT,25)
        draw_board = ImageDraw.Draw(chess_board)
        
        #draws the board
        for row in range(ROWS):
            for col in range(row%2,ROWS,2):
                square_coords =  (row*SQUARE_SIZE,col*SQUARE_SIZE,(row+1)*SQUARE_SIZE,(col+1)*SQUARE_SIZE)
                draw_board.rectangle(square_coords, fill = LIGHT_SQUARE)
        #draws the pieces
        for i in range(len(self.board)):
            for piece in self.board[i]:
                if piece == 0:
                    continue
                piece_pos = (piece.col*SQUARE_SIZE,piece.row*SQUARE_SIZE,(piece.col+1)*SQUARE_SIZE,(piece.row+1)*SQUARE_SIZE)
                piece_image = Image.open(piece.image)
                piece_resize = piece_image.resize((SQUARE_SIZE,SQUARE_SIZE))
                chess_board.paste(piece_resize,piece_pos,piece_resize.convert('RGBA'))
          
        for row in range(ROWS):
          if row%2 == 0:
            draw_board.text((5,row*SQUARE_SIZE),str(8-row),DARK_SQUARE,font=font)
          else:
            draw_board.text((5,row*SQUARE_SIZE),str(8-row),LIGHT_SQUARE,font=font)
        for col in range(COLS):
          if col%2 == 1:
            draw_board.text((col*SQUARE_SIZE+80,HEIGHT-30),str(chr(65+col)),DARK_SQUARE,font=font)
          else:
            draw_board.text((col*SQUARE_SIZE+80,HEIGHT-30),str(chr(65+col)),LIGHT_SQUARE,font=font)
        
        bytes_image = BytesIO()
        chess_board.save(bytes_image,format="PNG")
        bytes_image.seek(0)
        chess_board_file = discord.File(bytes_image,filename="chess_board.png")
       
        return chess_board_file


    
    def move_piece(self, piece, row, col):

        if piece != 0:
            piece.prev_move = (piece.row,piece.col)
            if piece.type == PieceTypes.Pawn:
                for t_piece in piece.take_piece:
                    if (row,col) != piece.take_pos[t_piece.col]:
                        continue
                    self.take_attacking_piece(piece,[t_piece.row,t_piece.col])
                    self.board[t_piece.row][t_piece.col] = 0
                    piece.take_piece = []
                    piece.take_pos = {}
                    break
                
            if piece.type == PieceTypes.King:
                if (row,col) in piece.castle_pos:
                    move_side = self._get_side(col,0)
                    for pos in piece.rook_pos:
                        castle_rook = self.get_piece(pos[0],pos[1])
                        if self._get_side(pos[1],0) != move_side:
                            continue
                        if castle_rook == 0:
                            continue
                        if castle_rook.moves != 0:
                            continue
                        
                        castle_rook_side = self._get_side(castle_rook.col,castle_rook)
                        self.board[castle_rook.row][castle_rook.col+(2*castle_rook_side)],self.board[castle_rook.row][castle_rook.col] = castle_rook,0
                        piece.move(castle_rook,castle_rook.row,castle_rook.col+(2*castle_rook_side))
                        piece.castle = False
                        piece.castled_rook = castle_rook
                        piece.castled_pos = pos
                        piece.castled = True
                        piece.rook_pos = []
            self.take_attacking_piece(piece,(row,col))
            self.board[piece.row][piece.col], self.board[row][col] =  0,  self.board[piece.row][piece.col]
            piece.move(piece,row,col)
            if piece.type == PieceTypes.Pawn:
                piece.check_in_passing(self.board)
                piece.stayed_moves = 0
                if piece.can_in_pass and (not piece in self.pawns_pass):
                    self.pawns_pass.append(piece)
            
        return 
    
    def create_board_pieces(self):
        for i in range(len(self.board)):
            if i+1 == 1 or i+1 == 2:
                color = 1
            elif i + 1 == 8 or i+1 == 7:
                color = 0
            for j in range(len(self.board)):
                if  i+1 == 1 or i+1 == 8:
                    if j+1 == 1 or j +1 == 8:
                        self.board[i][j] = Rook(i,j, color)
                    elif j+1 == 2 or j + 1 == 7:
                        self.board[i][j] = Knight(i,j,color)
                    elif j+1 == 3 or j +1 == 6:
                        self.board[i][j] = Bishop(i,j,color)
                    elif j+1 == 4:
                        self.board[i][j] = Queen(i,j,color)
                    elif j+1 == 5:
                        self.board[i][j] = King(i,j,color)
                        self.kings.append(self.board[i][j])
                if i+1 == 2 or i+1 == 7:
                    self.board[i][j] = Pawn(i,j,color)
        return
    def create_piece(self,piece_type,pawn):
        if piece_type == PieceTypes.Queen:
            self.board[pawn.row][pawn.col] = Queen(pawn.row,pawn.col,pawn.color)
        elif piece_type == PieceTypes.Bishop:
             self.board[pawn.row][pawn.col] = Bishop(pawn.row,pawn.col,pawn.color)
        elif piece_type == PieceTypes.Knight:
             self.board[pawn.row][pawn.col] = Knight(pawn.row,pawn.col,pawn.color)
        elif piece_type == PieceTypes.Rook:
             self.board[pawn.row][pawn.col] = Rook(pawn.row,pawn.col,pawn.color)
    def get_piece(self,row,col):
        print('here')
        print(self.board[row][col])
        return self.board[row][col]

    def remove(self, piece):
        self.board[piece.row][piece.col] = 0

    def get_valid_moves(self,piece, attacked):
        print('Inside valid moves function.')
        valid_moves = []
        legal_moves = []
        side_y = self._get_side(piece.row,piece)
        side_x = self._get_side(piece.col,piece)
        move_y,move_x,move_d = piece.get_moves()
        if piece.type == PieceTypes.Pawn:
            piece.take_piece = []
            piece.take_pos = {}
            if not attacked:
             valid_moves.extend(self.move(side_y,0,piece,move_y,MoveAxis.Y))
            if 0 <= piece.row+side_y <= 7 and 0 <= piece.col+side_x <= 7:
                attacking_piece = self.get_piece(piece.row+side_y,piece.col+side_x)
                if attacking_piece != 0:
                    if attacking_piece.color != piece.color:
                        valid_moves.append((piece.row+side_y,piece.col+side_x))
                     
                if attacked:
                    valid_moves.append((piece.row+side_y,piece.col+side_x))
            if 0 <= piece.row+side_y <= 7 and 0 <= piece.col-side_x <= 7:
                attacking_piece = self.get_piece(piece.row+side_y,piece.col-side_x)
                if attacking_piece != 0:
                    if attacking_piece.color != piece.color:
                        valid_moves.append((piece.row+side_y,piece.col-side_x))
                        
                        
                if attacked:
                    valid_moves.append((piece.row+side_y,piece.col-side_x))
            if 0 <= piece.col+side_x <= 7:
                attacking_piece = self.get_piece(piece.row,piece.col+side_x)
                if attacking_piece != 0:
                    if attacking_piece.type == PieceTypes.Pawn:
                        if attacking_piece.can_in_pass:
                            valid_moves.append((piece.row+side_y, piece.col+side_x))
                            if self.board[piece.row+side_y][piece.col+side_x] == 0:
                                piece.take_piece.append(attacking_piece)
                                piece.take_pos[attacking_piece.col] = (piece.row+side_y,piece.col+side_x)
                            
                                
                 
            if 0 <= piece.col-side_x <= 7:
                attacking_piece = self.get_piece(piece.row,piece.col-side_x)
                if attacking_piece != 0:
                    if attacking_piece.type == PieceTypes.Pawn:
                        if attacking_piece.can_in_pass:
                            valid_moves.append((piece.row+side_y, piece.col-side_x))
                            if self.board[piece.row+side_y][piece.col-side_x] == 0 :
                                piece.take_piece.append(attacking_piece)
                                piece.take_pos[attacking_piece.col] = (piece.row+side_y,piece.col-side_x)
                            
                                    
            if not attacked:
                legal_moves = self.get_legal_moves(piece,valid_moves)
                return legal_moves
        
            return valid_moves
        elif piece.type == PieceTypes.Knight:
            knight_moves = [[2,1], [-2,1],[2,-1],[-2,-1],[1,2],[-1,2],[1,-2],[-1,-2]]
            valid_moves = self.move_knight(piece,knight_moves)
            if not attacked:
                legal_moves = self.get_legal_moves(piece,valid_moves)
                return legal_moves
            return valid_moves
        if piece.type == PieceTypes.King:
            if piece.moves == 0 and piece.castled_rook != 0:
                castle_move = self.check_if_castle(piece)
                if piece.castle:
                    piece.castle_pos = castle_move
                    valid_moves.extend(castle_move)


        y_moves = []
        x_moves = []
        d_moves = []
        if move_y != 0:
            y_moves.extend(self.move(1,0,piece,move_y,MoveAxis.Y))
            y_moves.extend(self.move(-1,0,piece,move_y,MoveAxis.Y))
        if move_x != 0:
            x_moves.extend(self.move(1,0,piece,move_x,MoveAxis.X))
            x_moves.extend(self.move(-1,0,piece,move_x,MoveAxis.X))
        if move_d != 0:
            d_moves.extend(self.move(1,1,piece,move_d,MoveAxis.D))
            d_moves.extend(self.move(-1,1,piece,move_d,MoveAxis.D))
            d_moves.extend(self.move(1,-1,piece,move_d,MoveAxis.D))
            d_moves.extend(self.move(-1,-1,piece,move_d,MoveAxis.D))

        valid_moves.extend(y_moves)
        valid_moves.extend(x_moves)
        valid_moves.extend(d_moves)
            

        if not attacked:
            legal_moves = self.get_legal_moves(piece,valid_moves)
            return legal_moves
        return valid_moves
    
    def move(self,direction: int,direction_d :int,piece: Piece,move_amnt: int,move_axis: str):
        row_moves = []
        row = piece.row
        col = piece.col
        for i in range(1 ,move_amnt+1):
            if move_axis == MoveAxis.X:
                col = piece.col+(i*direction)
            elif move_axis == MoveAxis.Y:
                row = piece.row+(i*direction)
            elif move_axis == MoveAxis.D:
                row = piece.row+(i*direction)
                col = piece.col+(i*direction_d)
            if (0 <= row <= 7) and (0 <= col <= 7):
                current_pos = self.get_piece(row,col)
                if current_pos == 0:
                   
                    row_moves.append((row,col))
                else:
                    if piece.type == PieceTypes.Pawn:
                        break
                    if current_pos.color == piece.color:
                        break
                    elif current_pos.color != piece.color:
                        
                        row_moves.append((row,col))
                        break
           
        return row_moves
    def move_knight(self,piece, knight_moves):
        valid_moves= []
        for move in knight_moves:
                if (0 <= piece.row + move[1] <= 7) and (0 <= piece.col + move[0] <= 7):
                    current_pos = self.get_piece(piece.row + move[1], piece.col + move[0])
                    if current_pos == 0:
                        
                            valid_moves.append((piece.row + move[1], piece.col + move[0]))
                        
                    else:
                        if current_pos.color != piece.color:
                            valid_moves.append((piece.row + move[1], piece.col + move[0]))
        return valid_moves
            
    def check_if_castle(self, piece):
        moves= []
        moves_pos = self.move(1,0,piece,8,MoveAxis.X)
        moves_negitve = self.move(-1,0,piece,8,MoveAxis.X)
        side = self._get_side(piece.col,piece)
        piece.rook_pos = []
        if piece.moves != 0:
            return moves
       
        for i in range(len(moves_pos)):
            if moves_pos[i][1]+1 < 0 or moves_pos[i][1] +1 > 7:
                break
            curr_piece = self.get_piece(moves_pos[i][0],moves_pos[i][1]+1)
            if curr_piece == 0:
                continue
            if curr_piece.moves != 0 or curr_piece.type != PieceTypes.Rook:
                continue
            if curr_piece.color == piece.color:
                piece.castle = True
                piece.rook_pos.append((curr_piece.row,curr_piece.col))
                moves.append((moves_pos[i][0],piece.col + abs(moves_pos[i][1]-piece.col)))
                break
                        
        for i in range(len(moves_negitve)):
            if moves_negitve[i][1]-1 < 0 or moves_negitve[i][1] -1 > 7:
                break
            curr_piece = self.get_piece(moves_negitve[i][0],moves_negitve[i][1]-1)
            if curr_piece == 0:
                continue
        
            if curr_piece.type == PieceTypes.Rook and curr_piece.moves == 0 and curr_piece.color == piece.color:
                piece.castle = True
                piece.rook_pos.append((curr_piece.row,curr_piece.col))
                moves.append((moves_negitve[i][0],piece.col - abs(moves_negitve[i][1]-piece.col)))
                break
                
        if moves == []:
            self.castle = False    
            return []  
        return moves     
            
    def _get_side(self,axis,piece):
                    if piece != 0:
                        if piece.type == PieceTypes.Pawn:
                            if piece.color == 0:
                                return -1
                            else:
                                return 1
                    if  axis >= 4:
                        return -1
                    else:
                        return 1
                        
                    
                   
    def get_attacked_pieces(self,color):
            self.attacked_squares = []
            pieces = self.get_color_string(color)
            for piece in pieces:
                if piece != self.board[piece.row][piece.col]:
                    continue
                self.attacked_squares.extend(self.get_valid_moves(piece,True))
            return  self.attacked_squares
    def get_king(self,color):
        pieces = self.get_color_string(color)
        for i in range(len(pieces)):
            piece = pieces[i]
            if piece != 0:
                if piece.type == PieceTypes.King and piece.color == color:
                    return piece
    def check_if_check(self,color):
        king = self.get_king(color)
        self.check = False
        self.get_king_squares(king,color)
        return
       
    def get_king_squares(self,king,color):
        for i in self.king_attacked_squares:
            current_piece = self.get_piece(i[0],i[1])
            if current_piece != 0 and current_piece != None:
                if current_piece.color != color:
                    piece_attacked_squares = self.get_valid_moves(current_piece,True)
                    if (king.row,king.col) in piece_attacked_squares:
                        self.check = True
                        return True
        self.check = False
        return False
    def get_legal_moves(self,piece,valid_moves):
        curr_row = piece.row
        curr_col = piece.col
        check = self.check
        moves = piece.moves
        prev_move =piece.prev_move
        black_pieces = self.black_pieces_left
        white_pieces = self.white_pieces_left
        if piece.type == PieceTypes.Pawn:
                take_piece = piece.take_piece
                first_move = piece.first_move
                prev_move_amnt = piece.previous_move_amnt
                take_pos = piece.take_pos
                in_passing_turns = piece.in_passing_turns
                can_in_pass = piece.can_in_pass
                stayed_moves = piece.stayed_moves
        if piece.type == PieceTypes.King:
            castle = piece.castle
            rook_pos = piece.rook_pos
            castle_pos = piece.castle_pos
            castled = piece.castled
        legal_moves= []
        for move in valid_moves:
            capturing_piece = self.get_piece(move[0],move[1])
            self.move_piece(piece,move[0],move[1])
            self.check_if_check(piece.color)
            if not self.check:
                legal_moves.append(move)
            if piece.type == PieceTypes.Pawn:
                piece.take_piece = take_piece
            if piece.type == PieceTypes.King:
                piece.rook_pos = rook_pos
            self.simulate_undo_move(piece,capturing_piece,curr_row,curr_col)
            self.white_pieces_left = white_pieces
            self.black_pieces_left = black_pieces
            if piece.type == PieceTypes.Pawn:
                piece.take_piece = take_piece
                piece.take_pos = take_pos
                piece.first_move = first_move
                piece.previous_move_amnt = prev_move_amnt
                piece.in_passing_turns = in_passing_turns
                piece.can_in_pass = can_in_pass
                piece.stayed_moves = stayed_moves
            piece.moves = moves
            self.check = check
            
            piece.prev_move = prev_move
            if piece.type == PieceTypes.King:
                piece.rook_pos = rook_pos
                piece.castle = castle
                piece.castle_pos = castle_pos
                piece.castled = castled
                #piece.castled_rook = castled_rook
                #piece.castled_pos = castled_pos


       

        #piece.moves = moves
        #self.check = check
        return legal_moves

    def simulate_undo_move(self,selected_piece,capturing_piece,row,col):
        if selected_piece !=0:
            if selected_piece.type == PieceTypes.Pawn:
                for t_piece in selected_piece.take_piece:
                    if t_piece.col != selected_piece.col:
                        continue
                    self.board[t_piece.row][t_piece.col] = t_piece
                    self.append_piece(t_piece)
                    break
            if selected_piece.type == PieceTypes.King:
                if  selected_piece.moves == 1:
                    if selected_piece.castled_rook != None and selected_piece.castled_rook != 0:
                        castle_rook = self.get_piece(selected_piece.castled_rook.row, selected_piece.castled_rook.col)
                        if castle_rook.type == PieceTypes.Rook and castle_rook.moves == 1:
                            castle_rook_side = self._get_side(castle_rook.col,castle_rook)
                            self.board[castle_rook.row][castle_rook.col-(2*(castle_rook_side))],self.board[castle_rook.row][castle_rook.col] = castle_rook,0
                            selected_piece.move(castle_rook,castle_rook.row,castle_rook.col-(2*(castle_rook_side)))
                            castle_rook.moves = 0
                            selected_piece.castled_rook = None
                            selected_piece.castled_pos = None
            #capturing_piece.move(selected_piece.row,selected_piece.col)
            self.board[row][col],self.board[selected_piece.row][selected_piece.col] = selected_piece, capturing_piece
            selected_piece.move(selected_piece,row,col)
            if capturing_piece != 0:
                self.append_piece(capturing_piece)
            

                


    def check_if_promotion(self, color):
        outer_rows = [0,7]
        for row in outer_rows:
            for i in range(len(self.board)):
                piece = self.get_piece(row,i)
                if piece == 0:
                    continue
                if piece.type == PieceTypes.Pawn:
                    if piece.color == self.player_color or self.computer_color == None:
                        self.player_promotion = True
                        self.promotion_piece = piece
                    self.computer_promotion = True
                    self.promotion_piece = piece

                    return

    def update_pawn_pass(self):
        for pawn in self.pawns_pass:
            pawn.stayed_moves += 1
            if pawn.stayed_moves == 1:
                continue
            pawn.check_in_passing(self.board)
            if not pawn.can_in_pass:
                self.pawns_pass.remove(pawn)
    
    def get_all_valid_moves(self, color):
        total_moves = 0
        pieces = self.get_color_string(color)
        self.checkmate = False
        if not self.check:
            return
        for i in range(len(pieces)):
            piece = pieces[i]
            if piece != self.board[piece.row][piece.col]:
                continue
            piece.valid_moves = self.get_valid_moves(piece,False)
            total_moves += len(piece.valid_moves)
        if total_moves == 0:
            self.checkmate = True
            self.checkmate_color = color
            return True
        return False
    
    def get_black_and_white_pieces(self):
        black_pieces= 0
        white_pieces = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                piece = self.get_piece(i,j)
                if piece == 0:
                    continue
                if piece.color == 0:
                   self.white_board_pieces.append(piece)
                   continue
                self.black_board_pieces.append(piece)
    def take_attacking_piece(self,piece, taking_pos):
        taking_piece = self.get_piece(taking_pos[0],taking_pos[1])
        if taking_piece == 0 or taking_piece == None:
            return
        if taking_piece.color == 0:
            if taking_piece.color != piece.color :
                self.white_pieces_left -= 1
                self.white_board_pieces.remove(taking_piece)
            return
        if taking_piece.color != piece.color:
            self.black_pieces_left -= 1
            self.black_board_pieces.remove(taking_piece)

    
    def get_color_string(self,color):
        if color == 0:
           return self.white_board_pieces
        return self.black_board_pieces
    
    def append_piece(self,piece):
        if piece.color == 0:
            self.white_board_pieces.append(piece)
            self.white_pieces_left += 1
            return
        self.black_board_pieces.append(piece)
        self.black_pieces_left += 1
    def remove_piece(self,piece):
        if piece.color == 0:
            self.white_board_pieces.remove(piece)
            self.white_pieces_left -= 1
            return
        self.black_board_pieces.remove(piece)
        self.black_pieces_left -= 1
    
    def get_color_piece(self,piece):
        if piece.color == 0:
            for i in self.white_board_pieces:
                if i == piece:
                    return piece
        for i in self.black_board_pieces:
                if i == piece:
                    return piece
    