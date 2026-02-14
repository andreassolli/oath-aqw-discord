import discord
from discord import app_commands

from config import BANNED_LIST_CHANNEL_ID


def is_ban_channel():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.channel_id != BANNED_LIST_CHANNEL_ID:
            await interaction.response.send_message(
                "❌ This command can only be used in the designated moderation channel.",
                ephemeral=True,
            )
            return False
        return True

    return app_commands.check(predicate)
