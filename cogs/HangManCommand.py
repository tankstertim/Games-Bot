import discord 
from discord.ext import commands
from discord import app_commands
from game_files.game import Game
from other_files.enums import GameTypes
from buttons.VoteButtons import VoteButtons
import os
import json
class HangManCommands(commands.Cog):

  def __init__(self,client: commands.Bot):
    self.client = client
    self.send_private = True

    
  @commands.command()
  async def word(self,ctx,word : str):
    guild = ctx.guild
    user = ctx.message.author
    key = await self.client.get_server_key(guild)
    with open('server_info.json', 'r') as f:
      servers = json.load(f)
    game_channel = None
    if guild != None and str(guild.id) in servers:
      game_channel = servers[str(guild.id)]['game_channel']

    if key != None and str(ctx.channel.id) == game_channel:
    
      game = self.client.server_games[key]
      if game.game_choice != GameTypes.hm.value:
        await ctx.send('This server is not in a hangman game')
        return
      if game.turn != guild and game.game_choice != GameTypes.hm.value:
        await ctx.send("It is not your server's turn")
        return
      if game.turn == game.guild1:
        turn_channel = game.current_channel
      else:
        turn_channel = game.target_channel
      if ctx.channel != turn_channel and game.game_choice != GameTypes.hm.value:
        await ctx.send("It's  not your server's turn")
        return
      
      for letter in word:
        if letter == " ":
          continue
        if 97 <= ord(letter.lower()) <= 122:
          continue
        return 

      if game.mode == 2:
        game_word = game.game.set_word(word)
        if game_word != None:
          await ctx.send('The word can only have letters and spaces', ephemeral = self.send_private)
          return
        await self.client.server_update(game)
        return
      message = f"word {word}"
      vote_embed = discord.Embed(title = f"{user.name}'s move")
      vote_embed.set_thumbnail(url =f'{user.display_avatar}')
      vote_embed.add_field(name = 'Move', value =f'word: {word}')
      vote_view = VoteButtons(self.client, game,word, message)
      await ctx.send(embed=vote_embed,view=vote_view)
      return

    if ctx.guild != None:
      return
    if game_channel != None:
      if str(ctx.channel.id) == game_channel:
        await ctx.send("You can't play in this channel")
        return
    games = []
    for key in self.client.games.keys():
      if user == key[0] or user ==  key[1]:
        game = self.client.games[key]
        if game.game_choice != GameTypes.hm.value:
          continue
        if game.game.word != None:
          return
        games.append(key)

    if games == []:
      return

    guilds_embed = discord.Embed(title = 'Pick which server you want to use this word.', description='Type in a number.')
    for i in range(len(games)):
      curr_guild = self.client.get_guild(games[i][2])
      guilds_embed.add_field(name=f'{i+1}', value = f'{curr_guild.name}',inline = False)
    await ctx.send(embed=guilds_embed)
    try:
      while True:
        game_msg = await self.client.wait_for('message',check=lambda message: message.author == user,timeout=120)
        if game_msg == None:
          break
        if game_msg.content.isdigit() and 1 <= int(game_msg.content) <= len(games) :
          break
        await ctx.send('Not a valid input.')
    except:
      ctx.send('command timed out.')
      return
    game_content = game_msg.content
    guild_num = int(game_content)
    game = self.client.games[games[guild_num-1]]
    if not game.invite_accepted:
      await ctx.send('The invite has not been accepted.')
      return
    if user == game.p2:
      await ctx.send('You are not the creator of this game, only the creator can set the word.', ephemeral =self.send_private)
      return
    if game.game.word != None:
      await ctx.send('You have already picked a word.',ephemeral = self.send_private)
      return
  
    game_word = game.game.set_word(word)
    if game_word != None:
      await ctx.send('The word can only have letters and spaces', ephemeral = self.send_private)
      return
    await ctx.send(f'Word: {word}', ephemeral = self.send_private)
    await game.game.channel.send('The creator has chosen a word')
    curr_dir = os.getcwd()
    await game.game.channel.send(file = discord.File(os.path.join(curr_dir,f'assets/hangman{game.game.guesses}.png')))
    
    draw_message = game.draw()
    if draw_message != None:
      message = await game.game.channel.send(embed=draw_message)
      game.message = message


  
  @commands.command(name = 'guess')
  async def guess(self, ctx, letter: str):
    guild = ctx.guild
    user = ctx.message.author
    channel = ctx.channel
    key = await self.client.get_server_key(ctx.guild)
    with open('server_info.json', 'r') as f:
      servers = json.load(f)
    game_channel = None
    if str(ctx.guild.id) in servers:
      game_channel = servers[str(ctx.guild.id)]['game_channel']

    if key != None and str(ctx.channel.id) == game_channel:
      game = self.client.server_games[key]
      if game.turn != ctx.guild and game.game_choice != GameTypes.hm.value:
        return
      if game.turn == game.guild1:
        turn_channel = game.current_channel
      else:
        turn_channel = game.target_channel
      if ctx.channel != turn_channel and game.game_choice != GameTypes.hm.value:
        return
      if 97 > ord(letter.lower()) or 122 < ord(letter.lower()):
        return False
      if letter in game.game.used_letters:
        return

      if game.mode == 2:
        game.game.guess_letter(letter) 
        await self.client.server_update(game)
        return
      message = ctx.message.content[1::]
      vote_embed = discord.Embed(title = f"{ctx.message.author.name}'s move")
      vote_embed.set_thumbnail(url =f'{ctx.message.author.display_avatar}')
      vote_embed.add_field(name = 'Move', value =f'letter: {letter}')
      vote_view = VoteButtons(self.client, game,letter,message)
      await channel.send(embed=vote_embed,view=vote_view)
      return
    if game_channel != None:
      if str(ctx.channel.id) == game_channel:
        await ctx.reply("You can't play in this channel", ephemeral=True)
        return
    game_key = await self.client.get_key(user,guild.id)
    if game_key == None or self.client.games[game_key].game_type != 2:
      await ctx.reply('You are not in a hangman game, please use /help for commands.', ephemeral=self.send_private)
      return
    game = self.client.games[game_key]
    if game.game.creator == user:
      await  ctx.reply('The creator of the game can not guess a letter ',ephemeral =self.send_private)
      return
    if game.game.word == None:
      await ctx.reply('The creator of the game has not picked a word.',ephemeral=self.send_private)
      return
    if letter in game.game.used_letters:
      await ctx.reply('You have arleady used this letter', ephemeral =self.send_private)
      return
    game.game.guess_letter(letter) 
    curr_dir = os.getcwd()
    await ctx.send(file = discord.File(os.path.join(curr_dir,f'assets/hangman{game.game.guesses}.png')))
    game.message = await channel.send(embed=game.draw())
    winner_embed = await self.client.check_game_over(game,'scores.json')
    if winner_embed != None:
      await ctx.send(embed = winner_embed)
  
  @word.error
  async def word_handler(self,ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
      if error.param.name == 'word':
        await ctx.send("You forgot to type in a word. The command format should be !word your word here.")
  
  @guess.error
  async def guess_handler(self,ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
      if error.param.name == "letter":
        await ctx.send("you forgot to type in a letter. The command format should be !guess your letter here.")
  
async def setup(client:commands.Bot)-> None:
  await client.add_cog(HangManCommands(client))

