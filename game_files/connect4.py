import discord

class Connect4:

  def __init__(self,p1,p2):
    self.p1 = p1
    self.p2 = p2
    self.rows = 6
    self.cols = 7
    self.turn = p1
    self.board = [[':white_circle:' for j in range(self.cols)] for i in range(self.rows)]
    self.start_embed = discord.Embed(title = 'Connect4 Commands')
    self.start_embed.add_field(name = '!col', value = 'Type in !col (pos) to mark.')
    self.start_embed.add_field(name = '/quit', value = 'Type in /quit to leave the game.', inline = False)
    self.winner = None


  def move(self,col):
    if self.winner != None:
      return False
    i_list  = []
    for i in range(self.rows-1,-1,-1):
      i_list.append(i)
      if self.board[i][col-1] != ':white_circle:':
        continue
      if self.turn == self.p1:
        self.board[i][col-1] = ':yellow_circle:'
      elif self.turn == self.p2:
        self.board[i][col-1] = ':red_circle:'
      self.change_turn()
      print(i_list)
      return True
    return False

  def change_turn(self):
    self.check_win()
    if self.turn == self.p1:
      self.turn = self.p2
    elif self.turn == self.p2:
      self.turn = self.p1
      
  def check_win(self):
    open_spots = 0
    for i in range(self.rows):
      for j in range(self.cols):
        if self.board[i][j] == ':white_circle:':
          open_spots += 1
          continue
        #horizontal
        if j + 3 < self.cols:
          if self.board[i][j] == self.board[i][j+1] == self.board[i][j+2] == self.board[i][j+3]:
            self.winner = self.turn
            return True
        #vertical
        if i + 3 < self.rows:
          if self.board[i][j] == self.board[i+1][j] == self.board[i+2][j] == self.board[i+3][j]:
            self.winner = self.turn
            return True

        #diagonal 
        if i + 3 < self.rows and  j + 3 < self.cols:
          if self.board[i][j] == self.board[i+1][j+1] == self.board[i+2][j+2] == self.board[i+3][j+3]:
            self.winner= self.turn
            return True
        if i + 3  < self.rows and j -3 >= 0:
          if self.board[i][j] == self.board[i+1][j-1] == self.board[i+2][j-2] == self.board[i+3][j-3]:
            self.winner = self.turn
            return True
    if open_spots == 0:
      self.winner = 'tie'
      return True

    return False
        
        
    
  def draw(self):
    board_string = '' 
    for i in range(self.rows):
      for j in range(self.cols):
        board_string += self.board[i][j]
      board_string += '\n'
    return board_string 

