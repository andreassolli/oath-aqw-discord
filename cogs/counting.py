import discord
from discord.ext import commands

from config import COUNTING_CHANNEL_ID
from counting.handler import handle_counting_message


class CountingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id == COUNTING_CHANNEL_ID:
            await handle_counting_message(message)

        await self.bot.process_commands(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(CountingCog(bot))
