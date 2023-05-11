import discord
from discord.ext import commands
from discord import app_commands
from game_files.game  import Game
from buttons.InviteButtons import InviteButtons
from other_files.enums import GameTypes, GameNames
import json
class GenericCommands(commands.Cog):
  def __init__(self,client: commands.Bot):
    self.client = client
  
  @app_commands.command(name="help")
  @app_commands.describe(help_type = "Command Type")
  @app_commands.choices(help_type=[
    discord.app_commands.Choice(name="Normal MultiPlayer Commands", value = 1),
    discord.app_commands.Choice(name = "Server Duel Commands", value = 2),
    discord.app_commands.Choice(name = "Other Commands", value = 3)
  ])
  async def help(self,interaction, help_type: discord.app_commands.Choice[int]):
    if help_type.value == 1:
      help_embed = discord.Embed(title="Help")
      help_embed.add_field(name="----------------Normal MultiPlayer Commands----------------",value="",inline = False)
      help_embed.add_field(name = '/play', value = 'You can pick a game to play and the player you want to play against. If you want to play against the bot, use the bots name in the player argument.', inline = False)
      help_embed.add_field(name = '/quit', value = 'This command quits the game. if you are in the middle of the game you will loose elo.')
      help_embed.add_field(name = '/stats', value = 'This command shows your stats or can show other peoples stats. ', inline = False)
      help_embed.add_field(name = "Games to play", value = 'TicTacToe\nHangman\nConnect4', inline = False)
      help_embed.description =  '[Invite Bot](https://discord.com/api/oauth2/authorize?client_id=1074546275980152892&permissions=534723950656&scope=bot)'
      await interaction.response.send_message(embed=help_embed)
    elif help_type.value == 2:
      server_help_embed = discord.Embed(title="Help")
      server_help_embed.add_field(name = "----------------Server Duel Commands----------------",value="", inline = False)
      server_help_embed.add_field(name="/setchannel", value="sets your game channel so you can play with other servers. Only server admins or whitelisted roles can use this.",inline = False)
      server_help_embed.add_field(name="/serverduel", value="sends an invite to another server to play a game. Only server admins or whitelisted roles can play", inline = False)
      server_help_embed.add_field(name="/voteforfeit", value="starts a vote to forfeit vote. ", inline = False)
      server_help_embed.add_field(name="/serverstats", value="shows the servers stats.", inline =False)
      server_help_embed.add_field(name = "Games to play", value = 'TicTacToe\nHangman\nConnect4', inline = False)
      server_help_embed.description =  '[Invite Bot](https://discord.com/api/oauth2/authorize?client_id=1074546275980152892&permissions=534723950656&scope=bot)'
      await interaction.response.send_message(embed=server_help_embed)
    elif help_type.value == 3:
      other_help_embed = discord.Embed(title="Help")
      other_help_embed.add_field(name="----------------Other Commands----------------", value="",inline=False)
      other_help_embed.add_field(name="/leaderboard", value="shows the leaderboard of the top players globaly or localy in your server.",inline = False)
      other_help_embed.add_field(name="/addadminrole", value = "Allows you to whitelist a role. Only server admins or whitelisted roles can use this command.", inline =False)
      other_help_embed.add_field(name="/removeadminrole", value="Allows you to remove a role from the whitelist. Only servr admins or white listed roles can use this command.", inline=False)
      other_help_embed.add_field(name = "Games to play", value = 'TicTacToe\nHangman\nConnect4', inline = False)
      other_help_embed.description =  '[Invite Bot](https://discord.com/api/oauth2/authorize?client_id=1074546275980152892&permissions=534723950656&scope=bot)'
      await interaction.response.send_message(embed=other_help_embed)

  
    

  
  @app_commands.command(name="play", description = "play a game")
  @app_commands.describe(game = "Games to play")
  @app_commands.choices(game = [
    discord.app_commands.Choice(name="Tic Tac Toe", value = 1),
    discord.app_commands.Choice(name="Hangman", value = 2),
    discord.app_commands.Choice(name = 'Connect4', value = 3),
    discord.app_commands.Choice(name = 'Chess', value = 4)
  ])
  async def play(self,interaction, game: discord.app_commands.Choice[int], player: discord.Member):
    game_type = game.value
    guild_id = interaction.guild.id
    user = interaction.user
    channel = self.client.get_channel(interaction.channel.id)
    key = await self.client.get_key( user, guild_id)
    choice = game
    with open('server_info.json') as f:
      servers = json.load(f)
    if str(guild_id) in servers:
      if servers[str(guild_id)]['game_channel'] == str(interaction.channel.id):
        await interaction.response.send_message('You can not play in this channel', ephemeral = True)
        return
      
    if user == player:
      await interaction.response.send_message('You cant play yourself.', ephemeral = True)
      return
    if key != None:
      key_game = self.client.games[key]
      if guild_id == key_game.guild:
        await interaction.response.send_message(
          f'{user.mention}, your arleady in a game.')
        return
    if player == self.client.user:
      user_scores = await self.client.get_score(user)
      player_scores = await self.client.get_score(player)
      user_score = int(user_scores['tictactoe']['elo'])
      player_score = int(player_scores['tictactoe']['elo'])
      p1_prob = await  self.client.get_elo_prob(user_score,player_score)
      p2_prob = 1 - p1_prob
      self.client.games[(user, player, guild_id)] = Game(user, player, interaction.guild, True,game_type,channel,p1_prob,p2_prob)
      game = self.client.games[(user, player, guild_id)]
      with open("scores.json" , 'r') as f:
        users = json.load(f)
      if game_type == 1:
          users[str(game.p1.id)]['tictactoe']['games'] += 1
          users[str(game.p2.id)]['tictactoe']['games'] += 1
      else:
        await interaction.response.send_message(f'The bot cannot play {choice.name}.')
        return
      with open("scores.json" , "w") as f:
        json.dump(users,f,indent = 2)
      game = self.client.games[(user, player, guild_id)]
      user = interaction.user
      game.invite_accepted = True
      await interaction.response.send_message(f'Created a {choice.name} game for {user.mention} and {game.p2.mention}')
      await interaction.channel.send(embed = game.game.start_embed)
      draw_message = game.draw()
      if game_type == 4:
        await interaction.channel.send(file=draw_message)
        return
      if draw_message != None:
        board_message = await interaction.channel.send(draw_message)
        game.message = board_message
      return
    else:
      key =  await self.client.get_key( player, guild_id)
      if key != None:
        await interaction.response.send_message(
          "The player you want to play with is arleady in a game.",ephemeral = True)
        return
      user_scores = await self.client.get_score(user)
      player_scores = await self.client.get_score(player)
      if game_type == 1:
        user_score = int(user_scores['tictactoe']['elo'])
        player_score = int(player_scores['tictactoe']['elo'])
      elif game_type == 2:
        user_score = int(user_scores['hangman']['elo'])
        player_score = int(player_scores['hangman']['elo'])
      elif game_type == 3:
        user_score = int(user_scores['connect4']['elo'])
        player_score = int(player_scores['connect4']['elo'])
      elif game_type == 4:
        user_score = int(user_scores['chess']['elo'])
        player_score = int(player_scores['chess']['elo'])
      p1_prob = await self.client.get_elo_prob(user_score,player_score)
      p2_prob = 1 - p1_prob
      self.client.games[(user, player, guild_id)] = Game(user, player, interaction.guild, False, game_type,channel, p1_prob,p2_prob) 
     
    game = self.client.games[(user, player, guild_id)]
    invite_menu = InviteButtons(game,choice, self.client,game.p1,game.p2,interaction.guild)
    await invite_menu.send_invite(interaction)
  
  @app_commands.command(name='quit')
  async def quit(self,interaction):
    user = interaction.user
    key = await self.client.get_key(user, interaction.guild.id)
    if key not in self.client.games.keys():
      await interaction.response.send_message(
        'your not in a game.', ephemeral =True)
      return
    game = self.client.games[key]
    if game.game_choice == GameTypes.hm.value:
      game.winner  = 'tie'
    elif user == game.p2:
      game.winner = game.p1
    else: 
      game.winner = game.p2

    winner_embed  = await self.client.check_game_over(game,'scores.json')
    if winner_embed != None:
      await interaction.response.send_message(f'Game ended, {user.name} quit.', embed = winner_embed)
    

  @app_commands.command(name = 'stats')
  async def stats(self,interaction, player: discord.Member = None):
    if player == None:
      user = interaction.user
    else:
      user = player
    pfp = user.display_avatar
    score= await self.client.get_score(user)
    stats_embed = discord.Embed(title= "Stats")
    stats_embed.set_author(name = f"{user.name}")
    stats_embed.set_thumbnail(url=f"{pfp}")
    for k in GameTypes:
      stats_embed.add_field(name = k.value, value=f"""
        elo: {score[k.value]['elo']}
        wins: {score[k.value]['wins']}
        losses: {score[k.value]['losses']}
        draws: {score[k.value]['draws']}
        games played: {score[k.value]['games']}\n
        """, inline = True)
   
    
    await interaction.response.send_message(embed=stats_embed)
    



    
async def setup(client:commands.Bot)-> None:
  await client.add_cog(GenericCommands(client))