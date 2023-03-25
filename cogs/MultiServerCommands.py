import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.utils import get
from game_files.servergame import ServerGame
from buttons.InviteButtons import InviteButtons
from other_files.enums import GameTypes, GameNames, GameMode
from buttons.VoteButtons import *
from buttons.EmbedPageViews import *
from buttons.GeneralViews import *
import json
import math


class MultiServerCommands(commands.Cog):

  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name = "addadminrole")
  async def add_role(self,interaction,role: discord.Role):
    with open("server_info.json", "r") as f:
      servers = json.load(f)
    if not str(interaction.guild.id) in servers:
      await interaction.response.send_message('Your server does not have a game channel setup. Use \setchannel.')
      return
    user = interaction.user
    user_role = user.top_role
    guild = interaction.guild
    if not str(user_role.id) in servers[str(guild.id)]["whitelisted_roles"] and not user.guild_permissions.administrator:
      await interaction.response.send_message('You are not an admin of this server.')
      return
    if str(role.id) in servers[str(guild.id)]["whitelisted_roles"]:
      await interaction.response.send_message('This role is arleady whitelisted')
      return
    everyone_role = discord.utils.get(guild.roles,name="@everyone")
    if role == everyone_role:
      await interaction.response.send_message(f"You can not whitelist {role.name}")
      return
    servers[str(guild.id)]["whitelisted_roles"].append(str(role.id))
    with open("server_info.json", "w") as f:
      servers = json.dump(servers,f,indent=2)
    await interaction.response.send_message(f"{role.mention} has successfully been whitelisted")
  
  @app_commands.command(name='removeadminrole')
  async def remove_role(self, interaction,role: discord.Role):
    with open("server_info.json","r") as f:
      servers = json.load(f)
    
    if not str(interaction.guild.id) in servers:
      await interaction.response.send_message("Your server does not have a games channel setup. User /setchannel")
      return
    
    user = interaction.user
    user_role = user.top_role
    guild = interaction.guild
    if not str(user_role.id) in servers[str(guild.id)]['whitelisted_roles'] and not user.guild_permissions.administrator:
      await interaction.response.send_message('You are not an adminstrator of this server.')
      return
    
    if not str(role.id) in servers[str(guild.id)]['whitelisted_roles']:
      await interaction.response.send_message(f"{role.name} is not whitelisted.")
      return
    
    servers[str(guild.id)]['whitelisted_roles'].remove(str(role.id))
    with open("server_info.json", "w") as f:
      servers = json.dump(servers,f,indent=2)
    
    await interaction.response.send_message(f"{role.name} was successfully removed from the whitelist")

  @app_commands.command(
    name="setchannel",
    description="set the channel where server duel invites go")
  async def set_channel(self, interaction, channel: discord.TextChannel):
    if not interaction.user.top_role.permissions.administrator and  not interaction.user.guild_permissions.administrator:
      await interaction.followup.send("You are not a administrator of this server.")
      return
    with open('server_info.json', 'r') as f:
      servers = json.load(f)
    if str(interaction.guild.id) in servers.keys():
      servers[str(interaction.guild.id)]["game_channel"] = str(channel.id)
    else:
      game_dict = {}
      game_dict["game_channel"] = str(channel.id)
      for k in GameTypes:
        game_dict[k.value] = {
          'wins': 0,
          'losses': 0,
          'games': 0,
          'draws': 0,
          'elo': 1000
        }
      game_dict['whitelisted_roles'] = []
      servers[str(interaction.guild.id)] = game_dict
    await interaction.response.send_message('The invite channel has been set.')
    with open('server_info.json', 'w') as f:
      servers = json.dump(servers,f,indent= 2)
  @app_commands.command(name='leaderboard')
  @app_commands.describe(leaderboard_type="Type")
  @app_commands.choices(leaderboard_type=[
    discord.app_commands.Choice(name="Player", value=1),
    discord.app_commands.Choice(name="Server", value=2)
  ])
  @app_commands.describe(game_type="Game")
  @app_commands.choices(game_type=[
    discord.app_commands.Choice(name="Tic Tac Toe", value=GameTypes.ttt.value),
    discord.app_commands.Choice(name="Hangman", value=GameTypes.hm.value),
    discord.app_commands.Choice(name="Connnect 4", value=GameTypes.c4.value)
  ])
  async def leaderboard(self, interaction,
                        leaderboard_type: discord.app_commands.Choice[int],
                        game_type: discord.app_commands.Choice[str]):
    await interaction.response.defer()
    if leaderboard_type.value == 1:
      file_name = 'scores.json'
    elif leaderboard_type.value == 2:
      file_name = 'server_info.json'
    with open(file_name, 'r') as f:
      users_dict = json.load(f)
    if leaderboard_type.value == 1:
      dropdown_view = LeaderBoardDropdown(self.client,users_dict,game_type,leaderboard_type,interaction.channel)
      await dropdown_view.send()
      return
    elif leaderboard_type.value == 2:
      users = [
        self.client.get_guild(int(guild)) for guild in users_dict.keys()
      ]
    for i in range(len(users)):
      for j in range(len(users)):
        user1 = users_dict[str(users[i].id)][game_type.value]
        user2 = users_dict[str(users[j].id)][game_type.value]
        if user1['elo'] > user2['elo']:
          users[i], users[j] = users[j], users[i]

    leaderboard_view = LeaderBoardView(users, users_dict,
                                       leaderboard_type.value, game_type)
    await leaderboard_view.send(interaction.channel)

  @app_commands.command(name="serverduel", description="duel another server")
  @app_commands.describe(game="Games to play")
  @app_commands.choices(game=[
    discord.app_commands.Choice(name="Tic Tac Toe", value=1),
    discord.app_commands.Choice(name="Hangman", value=2),
    discord.app_commands.Choice(name='Connect4', value=3)
  ])
  @app_commands.describe(game_type="Mode")
  @app_commands.choices(game_type=[
    discord.app_commands.Choice(name="Vote", value=1),
    discord.app_commands.Choice(name="Chaos", value=2),
  ])
  async def server_duel(self, interaction,
                        game: discord.app_commands.Choice[int],
                        game_type: discord.app_commands.Choice[int],
                        server_name: str):
    await interaction.response.defer()
    if not interaction.user.top_role.permissions.administrator and  not interaction.user.guild_permissions.administrator:
      await interaction.followup.send("You are not a administrator of this server.")
      return
    with open("server_info.json", "r") as f:
      servers = json.load(f)
    guilds = [self.client.get_guild(int(guild)) for guild in servers.keys()]
    lst_guilds = []
    lst_ids = []
    for guild in guilds:
      if servers[str(guild.id)]['game_channel'] == None:
        continue
      guild_name = guild.name.lower().split()
      if server_name.lower().split() != guild_name:
        continue
      if interaction.guild == guild:
        continue
      lst_guilds.append(guild)
      lst_ids.append(guild.id)
    if lst_guilds == []:
      await interaction.followup.send(f'There is no server with the name {server_name} with this bot or has a game channel set up')
      return
    server_list = ServerListView(lst_guilds)
    await server_list.send(interaction.channel)
    await interaction.followup.send(
      "please copy and paste the id of the server.")
    try:
      while True:
        game_msg = await self.client.wait_for(
          'message',
          check=lambda message: message.author == interaction.user,
          timeout=120)
        if game_msg == None:
          break
        if game_msg.content.isdigit() and int(game_msg.content) in lst_ids:
          break
        await interaction.followup.send('Not a valid server id.')
    except:
      interaction.followup.send('command timed out.')
      return

    if not str(interaction.guild.id) in servers.keys():
      await interaction.followup.send(
        'Your server does not have an game channel set up.')
      return

    guilds = [guild for guild in self.client.guilds]
    server = self.client.get_guild(int(game_msg.content))
    choice = game.value
    key = await self.client.get_server_key(interaction.guild)
    if key != None:
      await interaction.followup.send('Your server is arleady in a duel')
      return
    if server == interaction.guild:
      await interaction.followup.send(
        'The other server cannot be the same server that you are in.')
      return
    if not str(server.id) in servers.keys():
      await interaction.followup.send(
        'The other server does not have a game channel set up.')
      return
    if servers[str(server.id)]['game_channel'] == None:
      await interaction.followup.send(
        'The other server does not have a game channel set up.')
      return
    server_key = await self.client.get_server_key(server)
    if server_key != None:
      await interaction.followup.send('The other server is arleady in a duel.')
      return
    target_channel_ids = [channel.id for channel in server.text_channels]
    current_channel_ids = [
      channel.id for channel in interaction.guild.text_channels
    ]
    if not int(servers[str(
        interaction.guild.id)]['game_channel']) in current_channel_ids:
      await interaction.followup.send(
        'This server does not have an game channel.')
      servers[str(interaction.guild.id)]['game_channel'] = None
      with open("server_info.json", "w") as f:
        json.dump(servers, f, indent=2)
      return
    if not int(servers[str(server.id)]['game_channel']) in target_channel_ids:
      await interaction.followup.send(
        'The other server does not have an game channel.')
      servers[str(server.id)]['game_channel'] = None
      with open("server_info.json", "w") as f:
        json.dump(servers, f, indent=2)
      return
    target_channel = self.client.get_channel(
      int(servers[str(server.id)]['game_channel']))
    current_channel = self.client.get_channel(
      int(servers[str(interaction.guild.id)]['game_channel']))
    current_server_permissions = current_channel.permissions_for(
      interaction.guild.me)
    target_server_permissions = target_channel.permissions_for(server.me)
    if not current_server_permissions.send_messages:
      await interaction.followup.send(
        "This server's game channel does not have permissions to send a message."
      )
      return
    if not target_server_permissions.send_messages:
      await interaction.channel.send(
        'The invite cannot be sent to the other server. Their game channel does not have permissions to send a message.'
      )
      return

    self.client.server_games[(interaction.guild, server)] = ServerGame(
      interaction.guild, server, choice, game_type.value, target_channel,
      current_channel)
    server_game = self.client.server_games[(interaction.guild, server)]
    await interaction.channel.send(
      f'Game Started please go to {current_channel.mention}')
    invite_view = VoteInviteButtons(self.client, choice, server_game)
    invite_embed = discord.Embed(title=f'Invite From {interaction.guild.name}')
    invite_embed.add_field(name='Server Id', value=f'{interaction.guild.id}')
    invite_embed.add_field(name='Game', value=f'{server_game.game_choice}')
    await target_channel.send(embed=invite_embed, view=invite_view)

  @app_commands.command(name='serverstats')
  async def stats(self, interaction):
    guild = interaction.guild
    score = await self.client.get_server_score(guild)
    if score == None:
      await interaction.response.send_message(
        'Your server does not have stats because it has not set up a game channel.'
      )
      return
    stats_embed = discord.Embed(title="Stats")
    stats_embed.set_author(name=f"{guild.name}")
    stats_embed.add_field(name='Tic Tac Toe',
                          value=f"""
      elo: {score['tictactoe']['elo']}
      wins: {score['tictactoe']['wins']}
      losses: {score['tictactoe']['losses']}
      draws: {score['tictactoe']['draws']}
      games played: {score['tictactoe']['games']}\n
      """,
                          inline=True)
    stats_embed.add_field(name='Hangman',
                          value=f"""
      elo: {score['hangman']['elo']}
      wins: {score['hangman']['wins']}
      losses: {score['hangman']['losses']}
      draws: {score['hangman']['draws']}
      games played: {score['hangman']['games']}\n
      """,
                          inline=True)
    stats_embed.add_field(name='Connect 4',
                          value=f"""
      elo: {score['connect4']['elo']}
      wins: {score['connect4']['wins']}
      losses: {score['connect4']['losses']}
      draws: {score['hangman']['draws']}
      games played: {score['connect4']['games']}\n
      """,
                          inline=True)
    await interaction.response.send_message(embed=stats_embed)

  @app_commands.command(name='serverlist')
  async def server_lst(self, interaction, search: str = None):
    await interaction.response.defer()
    with open('server_info.json', 'r') as f:
      servers = json.load(f)
    guilds = [self.client.get_guild(int(guild)) for guild in servers]
    if search != None:
      search_guilds = []
      for guild in guilds:
        if search in guild.name.lower():
          search_guilds.append(guild)
      list_view = ServerListView(search_guilds)
      await list_view.send(interaction.channel)
    else:
      list_view = ServerListView(guilds)
      await list_view.send(interaction.channel)

  @app_commands.command(name='voteforfeit')
  async def forfeit(self, interaction):
    with open('server_info.json') as f:
      servers = json.load(f)
    guild = interaction.guild
    key = await self.client.get_server_key(guild)
    if not str(guild.id) in servers:
      await interaction.response.send_message('Your server is not in a duel')
      return
    if servers[str(guild.id)]['game_channel'] != str(interaction.channel.id):
      await interaction.response.send_message(
        'You cant use this command in this channel.')
      return
    if key == None:
      await interaction.response.send_message('Your server is not in a duel')
      return
    game = self.client.server_games[key]
    await interaction.response.send_message('You have requested to forfeit.',
                                            ephemeral=True)
    quit_embed = discord.Embed(
      title=f'{interaction.user.name} wants to forfeit')
    quit_embed.set_thumbnail(url=f'{interaction.user.display_avatar}')
    quit_embed.add_field(name='forfeit',
                         value='if you forfeit you will lose elo.')
    quit_view = QuitVoteButtons(self.client, game, guild)
    await interaction.channel.send(embed=quit_embed, view=quit_view)
    return


async def setup(client: commands.Bot) -> None:
  await client.add_cog(MultiServerCommands(client))
