import discord
from discord.ext import commands
from discord import app_commands
from other_files.constants import *
from game_files.game import Game
from other_files.constants import *
from other_files.enums import GameNames,GameTypes
from buttons.VoteButtons import VoteButtons
import json



class ChessCommands(commands.Cog):
  def __init__(self,client: commands.Bot):
    self.client = client
  

  @commands.command(name='move')
  async def move(self,ctx, move: str):
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
      if game.mode == 2:
        is_move = game.game.move(move)
        if not is_move:
          await ctx.reply('Not a valild move. Please enter a number 1-9 that is empty',ephemeral = True)
          return
        await self.client.server_update(game)
        return
      
      message = ctx.message.content[1::]
      vote_embed = discord.Embed(title = f"{ctx.message.author.name}'s move")
      vote_embed.set_thumbnail(url =f'{ctx.message.author.display_avatar}')
      vote_embed.add_field(name = 'Move', value =f'move: {move}')
      vote_view = VoteButtons(self.client, game,move, message)
      await ctx.channel.send(embed=vote_embed,view=vote_view)
      return
    if game_channel != None:
      if str(ctx.channel.id) == game_channel:
        await ctx.send("You can't play in this channel")
        return
    user = ctx.message.author
    key = await self.client.get_key(user, ctx.guild.id)
    if key == None:
      await ctx.reply('Your not playing a game. Please create a game using /play',ephemeral=True)
      return
    game = self.client.games[key]
    if game.game_type != 4:
      await ctx.reply('Your not playing a chess game. Please create a game using /play',ephemeral=True)
      return
    if not game.invite_accepted:
      if game.p1 == user:
        await ctx.reply('The other player has not accepted the invite.')
      else:
        await ctx.reply('You have not accepted the invite')
      return
    if game.game.turn == 0:
      curr_turn = game.game.p1
    else:
      curr_turn = game.game.p2
    if curr_turn != user:
      await ctx.reply('It is Not your Turn')
      return
    print('going to move')
    is_move = game.game.move(move)
    print('done')
    print(is_move)
    if not is_move:
      await ctx.reply('Not a valild move. Please enter a number 1-9 that is empty')
      return
    await ctx.send(file=game.draw())
    winner_embed= await self.client.check_game_over(game,'scores.json')
    if winner_embed != None:
      await ctx.send(embed = winner_embed)
  @move.error
  async def place_handler(self,ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
      if error.param.name == "move":
        await ctx.send("you forgot to type in a moveition. The command format should be !place your moveition here.")

async def setup(client:commands.Bot)-> None:
  await client.add_cog(ChessCommands(client))