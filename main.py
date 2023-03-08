import os
import discord
import logging
import logging.handlers
import asyncio
from nbt import nbt
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

class NyaBot(commands.Bot):
	def __init__(self, command_prefix: str = "!"):
		super().__init__(command_prefix=command_prefix, case_insensitive=True, intents=discord.Intents.all())

	@staticmethod
	def is_owner():
		def owner(interaction: discord.Interaction):
			if interaction.user.id == 483721725205282858:
				return True
			else:
				return app_commands.MissingPermissions("Only the bot owner is allowed to use this command!")
		return app_commands.check(owner)

client = NyaBot()

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
	filename='logs/NyaBot.log',
	encoding='utf-8',
	maxBytes=32 * 1024 * 1024,  # 32 MiB
	backupCount=5,
)
dt_fmt = '%d-%m-%Y %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

discord.utils.setup_logging(handler=handler, formatter=formatter, level=logging.INFO, root=True)


async def run():
	def get_env() -> dict:
		load_dotenv()
		result = {
			"TOKEN": os.getenv("TOKEN")
		}
		return result

	environment = get_env()
	await client.start(environment["TOKEN"])

@client.event
async def setup_hook():
	print("NyaBot is now online!")

@client.command(name="sync")
@NyaBot.is_owner()
async def sync(ctx: commands.context.Context):
	synced = await client.tree.sync()
	await ctx.send(f"Synced {len(synced)} commands")

@client.command(name="biomenuke")
@app_commands.describe(
	dimension="The dimension that the biomes are in",
	namespace="The namespace of the biomes. Usually the mod's name.",
	data_file="Your level.dat file."
)
async def biomenuke(interaction: discord.Interaction, dimension: str, namespace: str, data_file: discord.Attachment):
	logging.info(f"Nuking biomes for user {interaction.message.author}")
	if not os.path.exists("./nuker/export/"):
		logger.info("Creating nuker directory..")
		os.makedirs("./nuker/export/")
	await data_file.save(fp="./nuker/export/temp.dat")

	nbtfile = nbt.NBTFile("./nuker/export/temp.dat", "rb")
	biomes_location = nbtfile["Data"]["WorldGenSettings"]["dimensions"][dimension]["generator"]["biome_source"]["biomes"]
	for index, tag in enumerate(biomes_location):
		biome = str(tag['biome']).split(":")
		if biome[0] == namespace:
			logger.debug(f"Nuking biome: {biome}")
			biomes_location[index].clear()
	nbtfile.write_file("./nuker/export/level.dat")
	logger.info("Biomes successfully nuked!")
	await interaction.message.reply("Biomes successfully nuked!", file=discord.File("./nuker/export/level.dat"))

if __name__ == "__main__":
	try:
		loop = asyncio.new_event_loop()
		loop.run_until_complete(run())
	except KeyboardInterrupt:
		logging.info("NyaBot going to sleep...")