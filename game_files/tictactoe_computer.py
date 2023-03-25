import time
import math
from other_files.constants import X,O,EMPTY_SQUARE



def computer_move(curr_pos, computer, player, depth):
    best_score = -math.inf
    best_move = None
    start_time = time.time()
    for i in range(len(curr_pos)):
        for j in range(len(curr_pos)):
            if curr_pos[i][j] != EMPTY_SQUARE:
                    continue
            curr_pos[i][j] = computer
            score = minimax(curr_pos,depth,-math.inf,math.inf,False, computer, player)
            curr_pos[i][j]  = EMPTY_SQUARE
            if score > best_score:
                best_score = score
                best_move = (i,j)
    end_time = time.time()
    final_time = end_time - start_time
    print(f'execution time: {final_time}')
   
    return best_move
    

def minimax(curr_pos,depth,alpha,beta,isMaximizing, computer, player):
    result = check_win(curr_pos)
    if  result == player:
        return -1 - depth
    if result == computer:
        return 1 + depth
    if result == 'tie':
        return 0
    if isMaximizing:
        best_score = -math.inf
        for i in range(len(curr_pos)):
            for j in range(len(curr_pos)):
                if curr_pos[i][j] != EMPTY_SQUARE:
                    continue
                curr_pos[i][j] = computer
                score = minimax(curr_pos,depth-1,alpha,beta,False, computer, player)
                curr_pos[i][j]  = EMPTY_SQUARE
                alpha = max(alpha,score)
                best_score = max(best_score,score)
                if beta <= alpha:
                    break
        return best_score
    else:
        best_score = math.inf
        for i in range(len(curr_pos)):
            for j in range(len(curr_pos)):
                if curr_pos[i][j] != EMPTY_SQUARE:
                    continue
                curr_pos[i][j] = player
                score = minimax(curr_pos,depth-1,alpha,beta,True, computer, player)
                curr_pos[i][j] = EMPTY_SQUARE
                best_score = min(score,best_score)
                beta = min(beta,score)
                if beta <= alpha:
                    break
        return best_score

def check_win(board):
        for i in range(len(board)):
            if board[i][0] == board[i][1] == board[i][2] and board[i][0] != EMPTY_SQUARE:
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] and board[0][i] != EMPTY_SQUARE:
                return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != EMPTY_SQUARE:
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != EMPTY_SQUARE:
            return board[0][2]
        openSpots= 0
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] != EMPTY_SQUARE:
                    openSpots += 1
        if openSpots == 9:
            return 'tie'
        return None
