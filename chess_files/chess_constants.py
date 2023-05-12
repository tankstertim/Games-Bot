import os

DARK_SQUARE  = (0, 198, 254)
LIGHT_SQUARE = (255,255,255)

ROWS,COLS = 8,8
HEIGHT, WIDTH = 800,800
SQUARE_SIZE = WIDTH//COLS
chess_dir = os.getcwd()
print(chess_dir)
BOARD_FONT = os.path.join(chess_dir,"chess_assets/Roboto-Bold.ttf")
BLACK_PAWN_IMAGE = os.path.join(chess_dir,"chess_assets/black_pawn.png")
BLACK_BISHOP_IMAGE = os.path.join(chess_dir,"chess_assets/black_bishop.png")
BLACK_KNIGHT_IMAGE = os.path.join(chess_dir,"chess_assets/black_knight.png")
BLACK_ROOK_IMAGE = os.path.join(chess_dir,"chess_assets/black_rook.png")
BLACK_QUEEN_IMAGE  = os.path.join(chess_dir,"chess_assets/black_queen.png")
BLACK_KING_IMAGE = os.path.join(chess_dir,"chess_assets/black_king.png")

WHITE_PAWN_IMAGE = os.path.join(chess_dir,"chess_assets/white_pawn.png")
WHITE_BISHOP_IMAGE = os.path.join(chess_dir,"chess_assets/white_bishop.png")
WHITE_KNIGHT_IMAGE = os.path.join(chess_dir,"chess_assets/white_knight.png")
WHITE_ROOK_IMAGE = os.path.join(chess_dir,"chess_assets/white_rook.png")
WHITE_QUEEN_IMAGE = os.path.join(chess_dir,"chess_assets/white_queen.png")
WHITE_KING_IMAGE = os.path.join(chess_dir,"chess_assets/white_king.png")