import discord
from game_files.game import Game
from other_files.enums import GameTypes
import json

class VoteInviteButtons(discord.ui.View):
  def __init__(self, client,game_type,game):
    super().__init__(timeout=30)
    self.value  = None
    self.game_type = game_type
    self.game = game
    self.client = client
    self.accept_votes = 0
    self.ignore_votes = 0
    self.voted_users = []
    self.used = False
  @discord.ui.button(label = 'Accept Invite(0)', style = discord.ButtonStyle.success)
  async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    user = interaction.user
    if user in self.voted_users:
      await interaction.response.send_message('You have arleady voted.', ephemeral = True)
      return 
    self.voted_users.append(user)
    self.accept_votes += 1
    button.label = f"Accept Invite({self.accept_votes})"
    await interaction.response.edit_message(view=self)
    return
  @discord.ui.button(label = 'Ignore Invite(0)', style = discord.ButtonStyle.danger)
  async def ingore_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    user = interaction.user
    if user in self.voted_users:
      await interaction.response.send_message('You have arleady voted.', ephemeral = True)
      return
    self.voted_users.append(user)
    self.ignore_votes += 1
    button.label = f'Accept Invite({self.ignore_votes})'
    await interaction.response.edit_message(view=self)
    return
  async def on_timeout(self):
    with open('server_info.json', 'r') as f:
      servers = json.load(f)
    server1_channels = [channel.id for channel in self.game.guild1.text_channels]
    server2_channels = [channel.id for channel in self.game.guild2.text_channels]
    if not self.game.current_channel.id in server1_channels:
      await self.game.target_channel.send('The invite was ignored channel.')
      return
    if not self.game.target_channel.id in server2_channels:
      await self.game.current_channel.send('The invite was ingored channel.')
      return
    s1_perms = self.game.current_channel.permissions_for(self.game.guild1.me)
    s2_perms = self.game.target_channel.permissions_for(self.game.guild2.me)
    if not s1_perms.send_messages:
      await self.game.target_channel.send('The invite was ignored')
      return
    if not s2_perms.send_messages:
      await self.game.current_channel.send('The invite was ingored')
      return
    key = await self.client.get_server_key(self.game.guild1)
    if self.accept_votes <= self.ignore_votes:
      await self.game.current_channel.send('The invite was ingored.')
      await self.game.target_channel.send('The invite was ingored.')
      await self.client.delete_server_game(key)
    elif self.accept_votes > self.ignore_votes:
      current = await self.client.get_server_score(self.game.guild1)
      target = await self.client.get_server_score(self.game.guild2)
      servers[str(self.game.guild1.id)][self.game.game_choice]['games'] += 1
      servers[str(self.game.guild2.id)][self.game.game_choice]['games'] += 1
      current_score = int(current[self.game.game_choice]['elo'])
      target_score = int(target[self.game.game_choice]['elo'])
      a_prob = await  self.client.get_elo_prob(current_score,target_score)
      b_prob = 1 - a_prob
      self.game.a_prob = a_prob
      self.game.b_prob = b_prob
      self.game.invite_accepted = True
      with open('server_info.json', 'w') as f:
        json.dump(servers,f,indent=2)
      message = 'The invite was  accepted.'
      board = self.game.draw()
      await self.game.current_channel.send(message)
      await self.game.target_channel.send(message)

      if self.game.game_choice == GameTypes.hm.value :
        await self.game.target_channel.send(embed = self.game.game.start_embed)
        await self.game.current_channel.send(embed =  self.game.game.start_embed)
        if self.game.game.word == None:
          if self.game.mode == 2:
            return
          await self.client.multi_move(self.game)
          return
      else:
        turn_embed = discord.Embed(title = 'Turn')
        if self.game.game_choice == GameTypes.chess.value:
          turn_embed.add_field(name='Server Id', value = f'{self.game.game.player_turn.id}')
          turn_embed.add_field(name = 'Server Name', value = f'{self.game.game.player_turn.name}')
        else:
          turn_embed.add_field(name='Server Id', value = f'{self.game.game.turn.id}')
          turn_embed.add_field(name = 'Server Name', value = f'{self.game.game.turn.name}')
        await self.game.target_channel.send(embed = self.game.game.start_embed)
        await self.game.current_channel.send(embed =  self.game.game.start_embed)
        await self.game.target_channel.send(embed = turn_embed)
        await self.game.current_channel.send(embed =  turn_embed)
        if  self.game.game_choice == GameTypes.chess.value:
          await self.game.current_channel.send(file=self.game.draw())
          await self.game.target_channel.send(file=self.game.draw())
        else:
          await self.game.current_channel.send(board)
          await self.game.target_channel.send(board)
      if self.game.mode == 2:
        return
      await self.client.multi_move(self.game)
      
 
  
    
class VoteButtons(discord.ui.View):
  def __init__(self,client,game,move,message):
    super().__init__()
    self.value = None
    self.game = game
    self.game_type= game.game_choice
    self.move = move
    self.message = message
    self.game.current_messages[message] = 0
    self.voted_users= []

  @discord.ui.button(label = "Votes(0)", style = discord.ButtonStyle.success)
  async def vote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    user = interaction.user
    if user in self.voted_users:
      await interaction.response.send_message('You have arleady voted', ephemeral = True)
      return 
    self.voted_users.append(user)
    self.game.current_messages[self.message] += 1
    button.label = f'Votes({self.game.current_messages[self.message]})'
    await interaction.response.edit_message(view=self)

class QuitVoteButtons(discord.ui.View):
  def __init__(self,client,game,guild):
    super().__init__(timeout=30)
    self.value = None
    self.game = game
    self.client = client
    self.server = guild
    self.voted_users = []
    self.accept_votes = 0
    self.ingnore_votes = 0
    

  @discord.ui.button(label = "Accept(0)", style=discord.ButtonStyle.success)
  async def accept_button(self,interaction:discord.Interaction,button: discord.ui.Button):
    user=interaction.user
    if user in self.voted_users:
      await interaction.response.send_message('You have arleady voted', ephemeral = True)
      return 
    self.voted_users.append(user)
    self.accept_votes+=1
    button.label = f'Accept({self.accept_votes})'
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Ignore(0)", style=discord.ButtonStyle.danger)
  async def ignore_button(self, interaction:discord.Interaction,button:discord.ui.Button):
    user=interaction.user
    if user in self.voted_users:
      await interaction.response.send_message('You have arleady voted', ephemeral = True)
      return 
    self.voted_users.append(user)
    self.ignore_votes+=1
    button.label = f'Ignore({self.ignore_votes})'
    await interaction.response.edit_message(view=self)

  async def on_timeout(self):
    if self.server == self.game.guild1:
      server_channel = self.game.current_channel
    else:
      server_channel = self.game.target_channel
    if self.accept_votes > self.ingnore_votes:
      if self.game.winner != None:
        print(None)
        return
      if self.server == self.game.guild1:
        self.game.winner = self.game.guild2
      elif self.server == self.game.guild2:
        self.game.winner = self.game.guild1
      await server_channel.send('Your server forfeited.')
      return                      
    