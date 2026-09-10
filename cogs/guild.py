import discord
from discord.ext import commands

from config import GUILD_LOG_CHANNEL_ID, TICKET_LOG_CHANNEL_ID, VERIFICATION_CHANNEL_ID
from guild.handler import handle_log


class GuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        channel = guild.get_channel(VERIFICATION_CHANNEL_ID)
        if not isinstance(channel, discord.TextChannel):
            return

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)

        try:
            await channel.purge(
                check=lambda m: member.id in m.raw_mentions,
            )
        except discord.Forbidden:
            if isinstance(log_channel, discord.TextChannel):
                await log_channel.send(
                    f"⚠️ Missing permissions to purge mention messages for "
                    f"{member} (`{member.id}`) after they left {channel.mention}."
                )
        except discord.HTTPException as e:
            if isinstance(log_channel, discord.TextChannel):
                await log_channel.send(
                    f"⚠️ Failed to purge mention messages for "
                    f"{member} (`{member.id}`) after they left {channel.mention}: {e}"
                )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.channel.id == GUILD_LOG_CHANNEL_ID:
            await handle_log(message)

        await self.bot.process_commands(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(GuildCog(bot))
