import discord
from discord import app_commands
from discord.ext import commands

class NyaBot(commands.Bot):
	def __init__(self, command_prefix: str = "!"):
		super().__init__(command_prefix=command_prefix, case_insensitive=True, intents=discord.Intents.all())

def is_owner():
    def owner(interaction: discord.Interaction):
        if interaction.user.id == 483721725205282858:
            return True
        else:
            return app_commands.MissingPermissions("Only the bot owner is allowed to use this command!")
    return app_commands.check(owner)
