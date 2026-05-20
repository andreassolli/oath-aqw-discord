import discord
from discord.ext import commands

from config import GUILD_LOG_CHANNEL_ID
from guild.handler import handle_log


class GuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id == GUILD_LOG_CHANNEL_ID:
            await handle_log(message)

        await self.bot.process_commands(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(GuildCog(bot))
