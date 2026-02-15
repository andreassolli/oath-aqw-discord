import discord
from discord import app_commands

from config import SPAM_BOTS_CHANNEL_ID, SPAM_CMD_CHANNEL_ID


def is_bot_channel():
    async def predicate(interaction: discord.Interaction) -> bool:
        allowed_channels = {SPAM_BOTS_CHANNEL_ID, SPAM_CMD_CHANNEL_ID}
        if interaction.channel_id not in allowed_channels:
            await interaction.response.send_message(
                "❌ This command can only be used in the designated moderation channel.",
                ephemeral=True,
            )
            return False
        return True

    return app_commands.check(predicate)
