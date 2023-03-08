import os
import discord
import logging
import logging.handlers
import asyncio
from nbt import nbt
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from libs import nyabot


client = nyabot.NyaBot()

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

cog_list = sorted([
	f"{file[:-3]}"
	for file in os.listdir("./cogs/")
	if file.endswith(".py")
])

async def run():
	def get_env() -> dict:
		load_dotenv()
		result = {
			"TOKEN": os.getenv("TOKEN")
		}
		return result

	environment = get_env()
	await client.start(environment["TOKEN"])

async def file_init():
	if not os.path.exists("./logs/"):
		os.mkdirs("./logs/")
		
	if not os.path.exists("./nuker/export/"):
		logging.info("Creating nuker directory..")
		os.makedirs("./nuker/export/")

@client.event
async def setup_hook():
	await file_init()
	
	for filename in os.listdir("./cogs/"):
		if filename.endswith(".py"):
			await client.load_extension(f"cogs.{filename[:-3]}")

	print("NyaBot is now online!")

@client.command(name="sync")
@nyabot.is_owner()
async def sync(ctx: commands.context.Context):
	synced = await client.tree.sync()
	await ctx.send(f"Synced {len(synced)} commands")
	

@client.event
async def on_command_error(ctx, error):
	raise error

if __name__ == "__main__":
	try:
		loop = asyncio.new_event_loop()
		loop.run_until_complete(run())
	except KeyboardInterrupt:
		logging.info("NyaBot going to sleep...")