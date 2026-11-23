import discord
from discord.ext import commands

from teamsync import config
from teamsync.db.connection import init_db

EXTENSIONS: list[str] = ["teamsync.cogs.decide"]


class TeamSyncBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())

    async def setup_hook(self):
        await init_db(config.DB_PATH)
        for ext in EXTENSIONS:
            await self.load_extension(ext)
        guild = discord.Object(id=config.GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)


bot = TeamSyncBot()


@bot.tree.command(name="ping", description="確認 bot 有在運作")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong", ephemeral=True)


@bot.event
async def on_ready():
    print(f"已登入：{bot.user}")


if __name__ == "__main__":
    bot.run(config.DISCORD_TOKEN)