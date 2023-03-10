import os
import discord
import logging
from discord import app_commands
from discord.ext import commands
from nbt import nbt
from libs import nyabot

class Utils(commands.Cog):
    def __init__(self, client: nyabot.NyaBot) -> None:
        self.client = client

    async def cog_load(self) -> None:
        logging.info(f"Cog: {self.__cog_name__} loaded")
    
    async def cog_unload(self) -> None:
        logging.info(f"Cog: {self.__cog_name__} unloaded")

    @app_commands.command(name="biomenuke", description="Removes biome entires from your level.dat")
    @app_commands.describe(
        dimension="The dimension that the biomes are in",
        namespace="The namespace of the biomes. Usually the mod's name.",
        data_file="The supplied level.dat file",
        public="Display result publicly."
    )
    async def biomenuke(self, interaction: discord.Interaction, dimension: str, namespace: str, data_file: discord.Attachment, public: bool = True) -> None:
        """Nukes biomes from a given level.dat file

        Args:
            dimension (str): The dimension that the biomes are in
            namespace (str): The namespace of the biomes. Ususallt the mod's name.
            data_file (discord.Attachment): The supplied level.dat file.
            public (bool): Display result publicly.
        """
        public = not public

        if not data_file.filename.endswith(".dat"):
            logging.error(f"Invalid .dat file! found {data_file.filename}")
            await interaction.response.send_message("Your attachment is not a valid level.dat file!", ephemeral=True)
            return
        
        await interaction.response.defer(thinking=True, ephemeral=public)

        await data_file.save(fp="./nuker/export/temp.dat")

        nbtfile = nbt.NBTFile("./nuker/export/temp.dat", "rb")
        biomes_location = nbtfile["Data"]["WorldGenSettings"]["dimensions"][dimension]["generator"]["biome_source"]["biomes"]
        for index, tag in enumerate(biomes_location):
            biome = str(tag['biome']).split(":")
            if biome[0] == namespace:
                logging.debug(f"Nuking biome: {biome}")
                biomes_location[index].clear()
        nbtfile.write_file("./nuker/export/level.dat")
        logging.info("Biomes successfully nuked!")
        await interaction.followup.send("Biomes successfully nuked!", file=discord.File("./nuker/export/level.dat"), ephemeral=public)

    @biomenuke.autocomplete("dimension")
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        dimensions = sorted(["minecraft:the_end", "minecraft:the_nether", "minecraft:overworld"])

        return [
            app_commands.Choice(name=dimension, value=dimension)
            for dimension in dimensions
            if current.replace(" ", "").lower() in dimension.replace(" ", "").lower()
        ]

async def setup(client: nyabot.NyaBot()) -> None:
    await client.add_cog(Utils(client))