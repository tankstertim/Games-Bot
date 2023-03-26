import discord
from discord.ext import commands
from discord import app_commands
from other_files.constants import *
from game_files.game import Game
from other_files.constants import *
from other_files.enums import GameNames,GameTypes
from buttons.VoteButtons import VoteButtons
import json
import dotmap


class TicTacToeCommands(commands.Cog):
  def __init__(self,client: commands.Bot):
    self.client = client
  
  @commands.command(name='place')
  async def place(self,ctx, pos: int):
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
      if pos > 9 or pos < 1:
        return
      if game.mode == 2:
        move = game.game.move(int(pos))
        if not move:
          await ctx.reply('Not a valild move. Please enter a number 1-9 that is empty',ephemeral = True)
          return
        await self.client.server_update(game)
        return
      
      message = ctx.message.content[1::]
      vote_embed = discord.Embed(title = f"{ctx.message.author.name}'s move")
      vote_embed.set_thumbnail(url =f'{ctx.message.author.display_avatar}')
      vote_embed.add_field(name = 'Move', value =f'pos: {pos}')
      vote_view = VoteButtons(self.client, game,pos, message)
      await ctx.channel.send(embed=vote_embed,view=vote_view)
      return
    if game_channel != None:
      if str(ctx.channel.id) == game_channel:
        await ctx.send("You can't play in this channel")
        return
    user = ctx.message.author
    key = await self.client.get_key(user, ctx.guild.id)
    if key == None:
      await ctx.reply('Your not playing a game. Please create a game using /tictactoe',ephemeral=True)
      return
    game = self.client.games[key]
    if game.game_type != 1:
      await ctx.reply('Your not playing a tictactoe game. Please create a game using /tictactoe',ephemeral=True)
      return
    if not game.invite_accepted:
      if game.p1 == user:
        await ctx.reply('The other player has not accepted the invite.')
      else:
        await ctx.reply('You have not accepted the invite')
      return
    if game.game.turn != user:
      await ctx.reply('It is Not your Turn',ephemeral = True)
      return
    if pos < 1 or pos > 9 or type(pos) != type(1):
        await ctx.reply('Not a valild move. Please enter a number 1-9 that is empty',ephemeral = True)
        return
    move = game.game.move(int(pos))
    if not move:
      await ctx.reply('Not a valild move. Please enter a number 1-9 that is empty',ephemeral = True)
      return
      game.message = None
    await ctx.send(game.draw())
    winner_embed= await self.client.check_game_over(game,'scores.json')
    if winner_embed != None:
      await ctx.send(embed = winner_embed)
  @place.error
  async def place_handler(self,ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
      if error.param.name == "pos":
        await ctx.send("you forgot to type in a position. The command format should be !place your position here.")
  
async def setup(client:commands.Bot)-> None:
  await client.add_cog(TicTacToeCommands(client))

