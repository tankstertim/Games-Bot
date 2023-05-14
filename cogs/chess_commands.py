import discord
from discord.ext import commands
from buttons.VoteButtons import VoteButtons
from other_files.enums import GameTypes
import json
class ChessCommands(commands.Cog):

  def __init__(self, client: commands.Bot):
    self.client = client
  
  @commands.command(name='move')
  async def move_chess(self,ctx,move_str:str):
    key = await self.client.get_server_key(ctx.guild)
    print('here')
    with open('server_info.json', 'r') as f:
      servers = json.load(f)
    game_channel = None
    if str(ctx.guild.id) in servers:
      game_channel = servers[str(ctx.guild.id)]['game_channel']
    print('not moving.')
    print(f'key: {key}')
    print(f'channel: {game_channel}, {ctx.channel}')
    if key != None and str(ctx.channel.id) == game_channel:
      print('inside')
      game = self.client.server_games[key]
      if game.turn != ctx.guild and game.game_choice != GameTypes.hm.value:
        print(game.turn.name, ctx.guild.name)
        print('exiting if not turn')
        return
      if game.turn == game.guild1:
        turn_channel = game.current_channel
      else:
        turn_channel = game.target_channel
      print('channel')
      if ctx.channel != turn_channel and game.game_choice != GameTypes.hm.value:
        print('exiting if current channel not equal to turn channel')
        return
      if game.mode == 2:
        move = game.game.move(move_str)
        if not move:
          await ctx.reply('Not a valild move.',ephemeral = True)
          return
        await self.client.server_update(game)
        return
      
      message = ctx.message.content[1::]
      vote_embed = discord.Embed(title = f"{ctx.message.author.name}'s move")
      vote_embed.set_thumbnail(url =f'{ctx.message.author.display_avatar}')
      vote_embed.add_field(name = 'Move', value =f'move: {move_str}')
      vote_view = VoteButtons(self.client, game,move_str, message)
      await ctx.channel.send(embed=vote_embed,view=vote_view)
      return
    if game_channel != None:
      if str(ctx.channel.id) == game_channel:
        await ctx.send("You can't play in this channel")
        return
    user = ctx.message.author
    key = await self.client.get_key(user, ctx.guild.id)
    if key == None:
      await ctx.reply('Your not playing a game. Please create a game using /play (game: Chess)',ephemeral=True)
      return
    game = self.client.games[key]
    if game.game_type != 4:
      await ctx.reply('Your not playing a chess game. Please create a game using /play (game: Chess)',ephemeral=True)
      return
    if not game.invite_accepted:
      if game.p1 == user:
        await ctx.reply('The other player has not accepted the invite.')
      else:
        await ctx.reply('You have not accepted the invite')
      return
    if game.game.player_turn != user:
      await ctx.reply('It is Not your Turn',ephemeral = True)
      return
    move = game.game.move(move_str)
    if not move:
      await ctx.reply('Not a valild move.',ephemeral = True)
      return
    
    board= game.draw()
    p1_score = await self.client.get_score(game.p1)
    p2_score = await self.client.get_score(game.p2)
    message = discord.Embed(title="Chess")
    message.add_field(name=f'{game.p1.name}',value=f"elo: {p1_score['chess']['elo']}\ncolor: white")
    message.add_field(name=f'{game.p2.name}',value=f"elo: {p2_score['chess']['elo']}\ncolor: black")
    message.add_field(name='turn',value=f"{game.game.player_turn}", inline = False)
    message.set_image(url="attachment://chess_board.png")
    await ctx.send(file=board,embed=message)
    winner_embed= await self.client.check_game_over(game,'scores.json')
    if winner_embed != None:
      await ctx.send(embed = winner_embed)
async def setup(client:commands.Bot)-> None:
  await client.add_cog(ChessCommands(client))