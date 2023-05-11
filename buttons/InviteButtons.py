import discord
from game_files.game import Game
from other_files.enums import GameTypes
import json
class InviteButtons(discord.ui.View):
  def __init__(self, game,game_type, client,creator,player,guild):
    super().__init__(timeout=30)
    self.value  = None
    self.game_type = game_type
    self.game = game
    self.creator = creator
    self.player = player
    self.client = client
    self.guild = guild
    self.message= None
    self.used = False
  @discord.ui.button(label = "Accept Invite", style = discord.ButtonStyle.success)
  async def accept_button(self,interaction: discord.Interaction, button: discord.ui.Button):
      user = interaction.user
      guild = interaction.guild
      self.game.invite_accepted = True
      game_key = await self.client.get_key(user,guild.id)
      if not game_key in self.client.games or self.used :
        await interaction.response.send_message('This invite is invalid')
        return  
      if user != self.player:
        await interaction.response.send_message('This invite is not for you.', ephemeral = True)
        return
      await interaction.channel.send(f'Created a {self.game_type.name} game for {user.mention} and {self.creator.mention}')
      with open("scores.json" , 'r') as f:
        users = json.load(f)
      if self.game.game_type == 1:
        users[str(self.creator.id)]['tictactoe']['games'] += 1
        users[str(self.player.id)]['tictactoe']['games'] += 1
      elif self.game.game_type == 2:
          users[str(self.creator.id)]['hangman']['games'] += 1
          users[str(self.player.id)]['hangman']['games'] += 1
      elif self.game.game_type == 3:
          users[str(self.creator.id)]['connect4']['games'] += 1
          users[str(self.player.id)]['connect4']['games'] += 1
      with open("scores.json" , "w") as f:
        json.dump(users,f,indent = 2)
      self.disable_view()
      await self.message.edit(view=self)
      await interaction.channel.send(embed = self.game.game.start_embed)
      if self.game.game_choice == GameTypes.hm.value:
        await interaction.channel.send(f'{self.creator.mention}, please use !word in private dms')
        await self.creator.send(f'{self.creator.mention}, please use !word (your word) here')
      draw_message = self.game.draw()
      self.value = False
      self.used = True
      if self.game.game_type == 4:
        await interaction.channel.send(file=draw_message)
        return
      if draw_message != None:
        board_message = await interaction.channel.send(draw_message)
        self.game.message = board_message
   

  @discord.ui.button(label = "Ignore Invite", style = discord.ButtonStyle.danger)
  async def ingore_button(self,interaction: discord.Interaction, button: discord.ui.Button):
    user = interaction.user
    guild = interaction.guild
    game_key = await self.client.get_key(user,guild.id)
    if not game_key in self.client.games or self.used :
        await interaction.response.send_message('This invite is invalid')
        return  
    if user != self.player:
      await interaction.response.send_message('you cannot ignore the invite.', ephemeral = True)
      return
    await self.client.delete_game(game_key)
    self.disable_view()
    await self.message.edit(view=self)
    await interaction.response.send_message('The invite was ignored')
    self.disabled = True
    self.value = False
    await self.message.edit(view=self)
    self.used = True

  @discord.ui.button(label = "Cancel Invite", style = discord.ButtonStyle.danger)
  async def cancel_button(self,interaction: discord.Interaction, button: discord.ui.Button):
    user = interaction.user
    guild = interaction.guild 
    game_key = await self.client.get_key(user,guild.id)
    if not game_key in self.client.games or self.used:
      await interaction.response.send_message('This invite is invalid')
      return
    if user != self.creator:
      await interaction.response.send_message('you cannot cancel this invite.')
      return 
    
    await self.client.delete_game(game_key)
    self.disable_view()
    await self.message.edit(view=self)
    await interaction.response.send_message('The invite was canceled.')
    self.value = False
    self.used = True
    

  def disable_view(self):
    for button in self.children:
      button.disabled = True
      
  async def send_invite(self,interaction):
    invite_embed = discord.Embed(title = f'{self.creator.name} has sent an invite to {self.player.name}')
    invite_embed.add_field(name = 'Game', value = self.game_type.name)
    invite_embed.add_field(name = 'Accept Invite', value = 'You have 30 seconds to accept the invite.')
    await interaction.response.send_message(embed = invite_embed,view=self)
    self.message = await interaction.original_response()
  async def on_timeout(self):
    if self.used:
      return
    self.disable_view()
    expired_embed = discord.Embed(title='Invite Expired')
    await self.message.edit(embed=expired_embed,view=self)
    game_key = await self.client.get_key(self.creator,self.guild.id)
    if game_key == None:
      return
    await self.client.delete_game(game_key)