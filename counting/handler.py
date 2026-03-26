import discord

from config import COUNTING_CHANNEL_ID

from .service import process_count_message


async def handle_counting_message(message: discord.Message):
    if message.channel.id != COUNTING_CHANNEL_ID:
        return

    is_valid = await process_count_message(message)

    if not is_valid:
        await message.delete()
        return

    await message.add_reaction("✅")
