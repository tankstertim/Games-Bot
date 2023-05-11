import discord
import asyncio
from discord import app_commands
from discord.ext import commands
#from Token_var import TOKEN
from game_files.game import Game
from .constants import *
import os
import math
import json
from .enums import GameTypes
from dotenv import load_dotenv


class Bot(commands.Bot):

  def __init__(self):
    super().__init__(command_prefix="!",intents=discord.Intents.all())
    self.cogslist = ["cogs.tictactoe_commands","cogs.GenericCommands","cogs.HangManCommand", "cogs.connect4_commands","cogs.MultiServerCommands","cogs.chess_commands"]
    self.games = {}
    self.server_games = {}

  async def on_ready(self):
    await self.tree.sync()
    print(f'Logged in as {self.user.name}')
    print(f'Amount of guilds: {len(self.guilds)}')
  
 
  
  async def setup_hook(self):
    for ext in self.cogslist:
      await self.load_extension(ext)
  
  async def get_key(self, player, guild_id):
    for key in self.games.keys():
      if (key[0] == player or key[1] == player) and guild_id == key[2]:
        return key
    return
  async def get_server_key(self, guild):
    for key in self.server_games.keys():
      if (key[0] == guild or key[1] == guild):
        return key
    return
  
  async def delete_game(self, games_key):
    if games_key in self.games.keys():
      self.games.pop(games_key)
  async def delete_server_game(self,key):
    if key in self.server_games.keys():
      self.server_games.pop(key)
  async def get_score(self,user):
    with open('scores.json', 'r') as f:
      users = json.load(f)

    game_dict = {}
    if str(user.id) in users:
      game_dict = users[str(user.id)]
    for k in GameTypes:
      if k.value in game_dict:
        print(k.value)
        continue
      game_dict[k.value] = {
        'wins': 0,
        'losses': 0,
        'games': 0,
        'draws': 0,
        'elo': 1000
        }
    if str(user.id) in users:
      if game_dict == users[str(user.id)]:
        return users[str(user.id)]
    users[str(user.id)] = game_dict
    with open('scores.json','w') as f:
      json.dump(users,f,indent=2)
    return users[str(user.id)]

  async def get_server_score(self,server):
    with open('server_info.json', 'r') as f:
      servers = json.load(f)
    game_dict = {}
    if str(server.id) in servers:
      servers_len = len(servers[str(server.id)])
    for k in GameTypes:
      if k.value in servers[str(server.id)]:
        print(k.value)
        continue
      servers[str(server.id)][k.value] = {
        'wins': 0,
        'losses': 0,
        'games': 0,
        'draws': 0,
        'elo': 1000
        }
    if servers_len == len(servers[str(server.id)]):
      print('exiting function')
      return servers[str(server.id)]
    with open('server_info.json','w') as f:
      json.dump(servers,f,indent=2)
    return servers[str(server.id)]




  async def get_elo_prob(self,a,b):
    return 1/(1+ (10**((b - a)/400)))


  async def check_game_over(self,game,file_name):
    game_choice = game.game_choice
    print(f'winner: {game.winner}')
    if game.winner != None:
      with open(file_name, 'r') as f:
        users = json.load(f)
      if file_name == 'server_info.json':
        player1 = game.guild1
        player2 = game.guild2
        player1_avatar = None
        player2_avatar = None
        user_scores = await self.get_server_score(player1)
        player_scores =await  self.get_server_score(player2)
      elif file_name == 'scores.json':
        player1 = game.p1
        player2 = game.p2
        player1_avatar = player1.display_avatar
        player2_avatar = player2.display_avatar
        user_scores = await self.get_score(player1)
        player_scores =await  self.get_score(player2)
      user_score = int(user_scores[game_choice]['elo'])
      player_score = int(player_scores[game_choice]['elo'])
      if game.winner == 'tie':
        a_score = 0.5
        b_score = 0.5
      elif game.winner == player1:
        a_score = 1
        b_score = 0
      elif game.winner == player2:
        a_score =0
        b_score =1
      new_player1_score = round(user_score + 32 * (a_score - game.a_prob))
      new_player2_score = round(player_score + 32 * (b_score - game.b_prob))
      users[str(player1.id)][game_choice]['elo'] = new_player1_score
      users[str(player2.id)][game_choice]['elo'] = new_player2_score

      if game.winner == 'tie':
        if file_name == "server_info.json":
          lose_embed = discord.Embed(title = 'The game was a draw.')
        winner_embed = discord.Embed(title = 'The game was a draw.')
      else:
        if file_name == "server_info.json":
          lose_embed = discord.Embed(title = f'The winner is {game.winner.name}')
        winner_embed = discord.Embed(title = f'The winner is {game.winner.name}')
      if a_score == 1:
        if player1_avatar == None:
          lose_embed.set_image(url="https://media.tenor.com/dF7OjuYn1s0AAAAC/text-animated-text.gif")
          winner_embed.set_image(url ="https://media.tenor.com/pJatGz_liCsAAAAC/congrats-congratulations.gif")
        else:
          winner_embed.set_image(url ="https://media.tenor.com/pJatGz_liCsAAAAC/congrats-congratulations.gif")
          winner_embed.set_thumbnail(url = f"{player1_avatar}")
        users[str(player1.id)][game_choice]['wins'] += 1
        users[str(player2.id)][game_choice]['losses'] += 1
      #https://media.tenor.com/AvtX2y2luhcAAAPo/almost-there.mp4
      elif b_score == 1:
        if player2_avatar == None:
          lose_embed.set_image(url="https://media.tenor.com/dF7OjuYn1s0AAAAC/text-animated-text.gif")
          winner_embed.set_image(url ="https://media.tenor.com/pJatGz_liCsAAAAC/congrats-congratulations.gif")
        else:
          winner_embed.set_image(url ="https://media.tenor.com/pJatGz_liCsAAAAC/congrats-congratulations.gif")
          winner_embed.set_thumbnail(url = f"{player2_avatar}")
        users[str(player1.id)][game_choice]['losses'] += 1
        users[str(player2.id)][game_choice]['wins'] += 1
      elif a_score == 0.5 and b_score == 0.5:
        if player1_avatar == None:
          lose_embed.set_image(url="https://media.tenor.com/AvtX2y2luhcAAAAC/almost-there.gif")
          winner_embed.set_image(url ="https://media.tenor.com/AvtX2y2luhcAAAAC/almost-there.gif")
        else:
          winner_embed.set_image(url ="https://media.tenor.com/AvtX2y2luhcAAAAC/almost-there.gif")
        users[str(player1.id)][game_choice]['draws'] += 1
        users[str(player2.id)][game_choice]['draws'] += 1
      
     
      user_value = f'old elo: {user_score}\nnew elo: {new_player1_score}\namount of elo gained: {new_player1_score - user_score}'
      player_value = f'old elo: {player_score}\nnew elo: {new_player2_score}\namount of elo gained: {new_player2_score - player_score}'

    
      
      winner_embed.add_field(name =f'{player1.name}', value = user_value)
      winner_embed.add_field(name =f'{player2.name}', value = player_value,inline = True)
      if player1_avatar == None:
        lose_embed.add_field(name =f'{player1.name}', value = user_value)
        lose_embed.add_field(name =f'{player2.name}', value = player_value,inline = True)
      
      with open(file_name , "w") as f:
        json.dump(users,f,indent = 2)
      if file_name == 'server_info.json':
        await self.delete_server_game((player1, player2))
        return winner_embed,lose_embed
      elif file_name == 'scores.json':
        await self.delete_game((player1, player2, game.guild.id))
      return winner_embed
    if file_name == 'server_info.json':
        return None,None
    return
  async def multi_move(self,server_game):
    
    winner_embed,lose_embed = await self.check_game_over(server_game,'server_info.json')
    if winner_embed != None:
      if server_game.winner == server_game.guild1:
        await server_game.current_channel.send(embed =winner_embed)
        await server_game.target_channel.send(embed=lose_embed)
        if server_game.game.winner == None:
          await server_game.current_channel.send(f'{server_game.guild2.name} forfeited')
          await server_game.target_channel.send(f'{server_game.guild2.name} forfeited')
      elif server_game.winner == server_game.guild2:
        await server_game.current_channel.send(embed =lose_embed)
        await server_game.target_channel.send(embed=winner_embed)
        if server_game.game.winner == None:
          await server_game.current_channel.send(f'{server_game.guild1.name} forfeited')
          await server_game.target_channel.send(f'{server_game.guild1.name} forfeited')
      elif server_game.winner == 'tie':
        await server_game.current_channel.send(embed =lose_embed)
        await server_game.target_channel.send(embed=winner_embed)
     
        
      await self.delete_server_game((server_game.guild1,server_game.guild2))
      return

    await asyncio.sleep(30)
    moves = server_game.current_messages
    max_votes = -math.inf
    max_msg = None
    for key in moves:
      if moves[key] > max_votes:
        max_votes = moves[key]
        max_msg = key
    if max_msg == None:
      return await self.multi_move(server_game)
      
    msg = max_msg.split()
    if server_game.game_choice == GameTypes.ttt.value:
      server_game.game.move(int(msg[1]))
    if server_game.game_choice == GameTypes.hm.value:
      if server_game.game.word == None:
        word = ""
        for i in range(1,len(msg)):
          word += f'{msg[i].lower()} '  
        server_game.game.set_word(word.strip(" "))
      else:
        server_game.game.guess_letter(msg[1].lower())
      server_game.current_messages= {}
      if server_game.game.word == None:
        return await self.multi_move(server_game)
      curr_dir = os.getcwd()
      await server_game.current_channel.send(file = discord.File(os.path.join(curr_dir,f'assets/hangman{server_game.game.guesses}.png')))
      await server_game.target_channel.send(file = discord.File(os.path.join(curr_dir,f'assets/hangman{server_game.game.guesses}.png')))
      await server_game.current_channel.send(embed=server_game.draw())
      await server_game.target_channel.send(embed=server_game.draw())
      return await self.multi_move(server_game)
        
    if server_game.game_choice == GameTypes.c4.value:
      server_game.game.move(int(msg[1]))
    
    server_game.current_messages= {}
    if server_game.game_choice != GameTypes.hm.value:
      turn_embed = discord.Embed(title = 'Turn')
      turn_embed.add_field(name='Server Id', value = f'{server_game.game.turn.id}')
      turn_embed.add_field(name = 'Server Name', value = f'{server_game.game.turn.name}')
      await server_game.target_channel.send(embed = turn_embed)
      await server_game.current_channel.send(embed =  turn_embed)
    if server_game.game_choice == GameTypes.chess.value:
      await server_game.target_channel.send(file=server_game.draw())
      await server_game.current_channel.send(file=server_game.draw())
      return await self.multi_move(server_game)
    await server_game.target_channel.send(server_game.draw())
    await server_game.current_channel.send(server_game.draw())
    return await self.multi_move(server_game)
  
  async def server_update(self,game):
    turn_embed = discord.Embed(title='Turn')
    if game.game_choice == GameTypes.chess.value:
      turn_embed.add_field(name='Server Id', value=f'{game.game.player_turn.id}')
      turn_embed.add_field(name='Server Name', value=f'{game.game.player_turn.name}')
      await game.current_channel.send(embed=turn_embed)
      await game.target_channel.send(embed=turn_embed)
    elif game.game_choice != GameTypes.hm.value:
      turn_embed.add_field(name='Server Id', value=f'{game.game.turn.id}')
      turn_embed.add_field(name='Server Name', value=f'{game.game.turn.name}')
      await game.current_channel.send(embed=turn_embed)
      await game.target_channel.send(embed=turn_embed)
    if game.game_choice == GameTypes.hm.value:      
      await game.current_channel.send(file=discord.File(f'hangman{game.game.guesses}.png'))
      await game.target_channel.send(file=discord.File(f'hangman{game.game.guesses}.png'))
      await game.current_channel.send(embed=game.draw())
      await game.target_channel.send(embed=game.draw())
    elif game.game_choice == GameTypes.chess.value:
      await game.current_channel.send(file=game.draw())
      await game.target_channel.send(file=game.draw())
    else:
      await game.current_channel.send(game.draw())
      await game.target_channel.send(game.draw())
    winner_embed,lose_embed= await self.check_game_over(game,'server_info.json')
    if winner_embed != None:
      if game.winner == game.guild1:
        await game.current_channel.send(embed = winner_embed)
        await game.target_channel.send(embed = lose_embed)
      elif game.winner == game.guild2:
        await game.current_channel.send(embed=lose_embed)
        await game.target_channel.send(embed =winner_embed)
      elif game.winner == 'tie':
        await game.current_channel.send(embed =winner_embed)
        await game.target_channel.send(embed=lose_embed)
    return
def run_bot():
  load_dotenv()
  TOKEN = os.getenv("TOKEN")
  client = Bot()
  client.run(TOKEN)

