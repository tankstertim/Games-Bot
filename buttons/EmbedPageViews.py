import discord
from discord.utils import get

class ServerListView(discord.ui.View):

  def __init__(self, guilds):
    super().__init__()
    self.current_page = 1
    self.guilds = guilds
    self.sep = 5

  async def send(self, ctx):
    self.message = await ctx.send(view=self)
    await self.update_message(self.guilds[:self.sep])

  def create_embed(self, data):
    embed = discord.Embed(
      title='Servers',
      description=
      f"page {self.current_page} of {int(len(self.guilds) / self.sep) + 1}")
    for item in data:
      embed.add_field(name=item.name, value=item.id, inline=False)
    return embed

  async def update_message(self, data):
    self.update_buttons()
    await self.message.edit(embed=self.create_embed(data), view=self)

  def update_buttons(self):
    if self.current_page == 1:
      self.start_button.disabled = True
      self.prev_button.disabled = True
    else:
      self.start_button.disabled = False
      self.prev_button.disabled = False

    if self.current_page == int(len(self.guilds) / self.sep) + 1:
      self.next_button.disabled = True
      self.last_button.disabled = True
    else:
      self.next_button.disabled = False
      self.last_button.disabled = False

  @discord.ui.button(label="|<", style=discord.ButtonStyle.primary)
  async def start_button(self, interaction: discord.Interaction,
                         button: discord):
    await interaction.response.defer()
    self.current_page = 1
    until_item = self.current_page * self.sep
    from_item = until_item - self.sep
    await self.update_message(self.guilds[:until_item])

  @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
  async def prev_button(self, interaction: discord.Interaction,
                        button: discord):
    await interaction.response.defer()
    self.current_page -= 1
    until_item = self.current_page * self.sep
    from_item = until_item - self.sep
    await self.update_message(self.guilds[from_item:until_item])

  @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
  async def next_button(self, interaction: discord.Interaction,
                        button: discord):
    await interaction.response.defer()
    self.current_page += 1
    until_item = self.current_page * self.sep
    from_item = until_item - self.sep
    await self.update_message(self.guilds[from_item:until_item])

  @discord.ui.button(label=">|", style=discord.ButtonStyle.primary)
  async def last_button(self, interaction: discord.Interaction,
                        button: discord):
    await interaction.response.defer()
    self.current_page = int(len(self.guilds) / self.sep) + 1
    until_item = self.current_page * self.sep
    from_item = until_item - self.sep
    await self.update_message(self.guilds[from_item:])


class LeaderBoardView(discord.ui.View):

  def __init__(self, users, users_dict,leaderboard_type, game_type):
    super().__init__()
    self.current_page = 1
    self.users = users
    self.sep = 3
    self.leaderboard_type = leaderboard_type
    self.users_dict = users_dict
    self.game_type = game_type
  async def send(self, ctx):
    self.message = await ctx.send(view=self)
    await self.update_message(self.users[:self.sep])

  def create_embed(self, data):
    if self.leaderboard_type == 1:
      embed = discord.Embed(
        title='Player Leaderboard',
        description=
        f"{self.game_type.name}\n\npage {self.current_page} of {int(len(self.users) / self.sep) + 1}")
    elif self.leaderboard_type == 2:
        embed = discord.Embed(
        title='Server Leaderboard',
        description=
        f"{self.game_type.name}\n\npage {self.current_page} of {int(len(self.users) / self.sep) + 1}")
    i = (self.current_page*3)-2
    for user in data:
      if self.leaderboard_type == 1:
        user_info = self.users_dict[str(user.id)][self.game_type.value]
        embed.add_field(name=f'{i}. {user.name}', value=f"""
        elo: {user_info['elo']}
        wins: {user_info['wins']}
        losses: {user_info['losses']}
        draws: {user_info['draws']}
        games played: {user_info['games']}
        """, inline=False)
      elif self.leaderboard_type == 2:
        user_info = self.users_dict[str(user.id)][self.game_type.value]
        embed.add_field(name=f'{i}. {user.name}', value=f"""
        server id: {user.id}
        elo: {user_info['elo']}
        wins: {user_info['wins']}
        losses: {user_info['losses']}
        draws: {user_info['draws']}
        games played: {user_info['games']}
        """, inline=False)
        
      i+=1
    return embed

  async def update_message(self, data):
    self.update_buttons()
    await self.message.edit(embed=self.create_embed(data), view=self)

  def update_buttons(self):
    if self.current_page == 1:
      self.start_button.disabled = True
      self.prev_button.disabled = True
    else:
      self.start_button.disabled = False
      self.prev_button.disabled = False

    if self.current_page == int(len(self.users) / self.sep) + 1:
      self.next_button.disabled = True
      self.last_button.disabled = True
    else:
      self.next_button.disabled = False
      self.last_button.disabled = False

  @discord.ui.button(label="|<", style=discord.ButtonStyle.primary)
  async def start_button(self, interaction: discord.Interaction,
                         button: discord):
    await interaction.response.defer()
    self.current_page = 1
    until_item = self.current_page * self.sep
    from_item = until_item - self.sep
    await self.update_message(self.users[:until_item])

  @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
  async def prev_button(self, interaction: discord.Interaction,
                        button: discord):
    await interaction.response.defer()
    self.current_page -= 1
    until_item = self.current_page * self.sep
    from_item = until_item - self.sep
    await self.update_message(self.users[from_item:until_item])

  @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
  async def next_button(self, interaction: discord.Interaction,
                        button: discord):
    await interaction.response.defer()
    self.current_page += 1
    until_item = self.current_page * self.sep
    from_item = until_item - self.sep
    await self.update_message(self.users[from_item:until_item])

  @discord.ui.button(label=">|", style=discord.ButtonStyle.primary)
  async def last_button(self, interaction: discord.Interaction,
                        button: discord):
    await interaction.response.defer()
    self.current_page = int(len(self.users) / self.sep) + 1
    until_item = self.current_page * self.sep
    from_item = until_item - self.sep
    await self.update_message(self.users[from_item:])
