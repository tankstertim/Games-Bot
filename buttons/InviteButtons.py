import discord
from game_files.game import Game
from other_files.enums import GameTypes
import json
class InviteButtons(discord.ui.View):
  def __init__(self, game,game_type, client):
    super().__init__(timeout=30)
    self.value  = None
    self.game_type = game_type
    self.game = game
    self.client = client
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
      if user != self.game.p2:
        await interaction.response.send_message('This invite is not for you.', ephemeral = True)
        return
      await interaction.channel.send(f'Created a {self.game_type.name} game for {user.mention} and {self.game.p1.mention}')
      with open("scores.json" , 'r') as f:
        users = json.load(f)
      if self.game.game_type == 1:
        users[str(self.game.p1.id)]['tictactoe']['games'] += 1
        users[str(self.game.p2.id)]['tictactoe']['games'] += 1
      elif self.game.game_type == 2:
          users[str(self.game.p1.id)]['hangman']['games'] += 1
          users[str(self.game.p2.id)]['hangman']['games'] += 1
      elif self.game.game_type == 3:
          users[str(self.game.p1.id)]['connect4']['games'] += 1
          users[str(self.game.p2.id)]['connect4']['games'] += 1
      with open("scores.json" , "w") as f:
        json.dump(users,f,indent = 2)
      await self.disable_view()
      await interaction.response.edit_message(view=self)
      await interaction.channel.send(embed = self.game.game.start_embed)
      if self.game.game_choice == GameTypes.hm.value:
        await interaction.channel.send(f'{self.game.p1.mention}, please use !word in private dms')
        await self.game.p1.send(f'{self.game.p1.mention}, please use !word (your word) here')
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
    if user != self.game.p2:
      await interaction.response.send_message('The creator of the game cannot ignore the invite.', ephemeral = True)
      return
    await self.client.delete_game(game_key)
    await self.disable_view()
    await interaction.response.edit_message(view=self)
    await interaction.response.send_message('The invite was ignored')
    self.disabled = True
    self.value = False
    for button in self.children:
      button.disabled =True
      print(button.disabled)
    self.used = True

  @discord.ui.button(label = "Cancel Invite", style = discord.ButtonStyle.danger)
  async def cancel_button(self,interaction: discord.Interaction, button: discord.ui.Button):
    user = interaction.user
    guild = interaction.guild 
    game_key = await self.client.get_key(user,guild.id)
    if not game_key in self.client.games or self.used:
      await interaction.response.send_message('This invite is invalid')
      return
    if user != self.game.p1:
      await interaction.response.send_message('Only the creator of this invite can cancel it.')
      return 
    
    await self.client.delete_game(game_key)
    await self.disable_view()
    await interaction.response.edit_message(view=self)
    await interaction.channel.send('The invite was canceled.')
    self.value = False
    self.used = True

  async def disable_view(self):
    for button in self.children:
      button.disabled = True
    