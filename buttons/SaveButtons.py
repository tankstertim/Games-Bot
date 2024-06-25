import discord
from discord.ui import Button,View
from game_files.game import Game
from other_files.enums import GameTypes
import json

class SaveButtons(View):
    def __init__(self, client,game_type,game,player):
        super().__init__(timeout=30)
        self.value = None
        self.game_type = game_type
        self.game = game
        self.client = client
        self.player = player
    
    @discord.ui.button(label="save", style=discord.ButtonStyle.success)
    async def save_button(self,interaction: discord.Interaction, button: Button):
        if self.game.saved:
            return
        if interaction.user != self.game.p1 and interaction.user != self.game.p2:
            return
        if interaction.user == self.player:
            return
        key = await self.client.get_key(interaction.player,interaction.guild.id)
        await self.client.delete_game(key)
        self.client.saved_games[key] = self.game
        self.saved = True
        
