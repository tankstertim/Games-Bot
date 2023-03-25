import discord
from game_files.game import Game
from other_files.enums import GameTypes
from .EmbedPageViews import LeaderBoardView
from discord.ui import View
import json

class LeaderBoardDropdown(discord.ui.Select):
  def __init__(self,client,users_dict,game_type,leaderboard_type,ctx):
    self.client = client
    self.users_dict = users_dict
    self.game_type = game_type
    self.leaderboard_type= leaderboard_type
    self.ctx = ctx
    options = [
      discord.SelectOption(label = 'Local',value = "1", description="Shows players only in this server."),
      discord.SelectOption(label = 'Global', value = "2",description = "Shows all players that use this bot.")
    ]
    super().__init__(placeholder="Select which player leaderboard you want to view",options=options,min_values=1,max_values=1)
  async def send(self):
    view = View()
    view.add_item(self)
    self.message = await self.ctx.send(view=view)
  
  async def disable_select_menu(self, interaction):
    self.disabled = True
    view = View()
    view.add_item(self)


  
  async def callback(self,interaction: discord.Interaction):
    if self.values[0] == "1":
      users = []
      for member in interaction.guild.members:
        if not str(member.id) in self.users_dict.keys():
          continue
        users.append(member)
    else:
      users = [
        await self.client.fetch_user(int(user)) for user in self.users_dict.keys()
      ]
    for i in range(len(users)):
      for j in range(len(users)):
        user1 = self.users_dict[str(users[i].id)][self.game_type.value]
        user2 = self.users_dict[str(users[j].id)][self.game_type.value]
        if user1['elo'] > user2['elo']:
          users[i], users[j] = users[j], users[i]

    leaderboard_view = LeaderBoardView(users, self.users_dict,
                                       self.leaderboard_type.value, self.game_type)
    self.disabled = True
    view = View()
    view.add_item(self)
    await interaction.response.edit_message(view=view)
    await leaderboard_view.send(interaction.channel)
class DropdownView(discord.ui.View):
  def __init__(self,client,users_dict,game_type,leaderboard_type):
    super().__init__()
    self.add_item(LeaderBoardDropdown(client,users_dict,game_type,leaderboard_type))