from config import GUILD_LOG_CHANNEL_ID
from firebase_client import db
from guild.service import process_log


async def handle_log(message: discord.Message):
    if message.channel.id != GUILD_LOG_CHANNEL_ID:
        return

    event = await process_log(message)

    if not event:
        return

    await message.add_reaction("✅")
