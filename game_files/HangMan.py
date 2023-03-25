import discord



class HangMan:
  def __init__(self,creator,player, channel):
    self.player = player
    self.creator = creator
    self.found_letters = []
    self.used_letters = []
    self.word = None
    self.word_guess = ""
    self.word_size = 0
    self.winner = None 
    self.guesses = 7
    self.channel = channel
    self.start_embed = discord.Embed(title = "Hangman Commands")
    self.start_embed.add_field(name= '!word', value = "creator of the game can choose the word", inline = False)
    self.start_embed.add_field(name = "!guess", value = "guess a letter", inline = False)
    self.start_embed.add_field(name = "/quit", value=  "leave the game", inline= False)

  def set_word(self,word):
    for letter in word:
      if letter == " ":
        continue
      if 97 <= ord(letter.lower()) <= 122:
        continue
      return "The word can only have letters and spaces. It can't have numbers or other characters."
    self.word = word.lower()
    self.word_size = len(word)
    for letter in word:
      if letter == " ":
        self.word_size -= 1
        continue
    return 

  
  def guess_letter(self,g_letter):
    correct_letters = 0
    if 97 > ord(g_letter.lower()) or 122 < ord(g_letter.lower()):
      return False
    self.used_letters.append(g_letter.lower())
    for letter in self.word:
      if letter == g_letter.lower():
        self.found_letters.append(letter)
        correct_letters += 1
    if correct_letters == 0:
      self.guesses -= 1
      if self.guesses == 0:
        self.winner = self.creator
      return False
    if len(self.found_letters) == self.word_size:
      self.winner = self.player
    return True
  
  def draw(self):
    if self.word == None:
      return
    word_message = ""
    for letter in self.word:
      if letter == " ":
        word_message += ":white_large_square:"
        continue
      if letter in self.found_letters:
        word_message += f":regional_indicator_{letter}:"
      else:
        word_message += ":blue_square:"
    g_letters = ''
    for letter in self.used_letters:
      g_letters += f":regional_indicator_{letter}:"
      if self.used_letters[-1] != letter:
        g_letters += ','
    draw_embed = discord.Embed(title = "HangMan")
    draw_embed.add_field(name = 'Word', value = word_message)
    draw_embed.add_field(name= 'Guessed Letters', value = g_letters, inline = False)
    return draw_embed
    
