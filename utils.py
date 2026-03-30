import discord
from discord import app_commands

from config import SPAM_BOTS_CHANNEL_ID, SPAM_CMD_CHANNEL_ID
from firebase_client import db


def load_words(filepath: str) -> list[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


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


async def unlock_all_coins():
    users_ref = db.collection("users")
    docs = users_ref.where("locked_coins", ">", 0).stream()

    batch = db.batch()
    count = 0

    for doc in docs:
        batch.update(users_ref.document(doc.id), {"locked_coins": 0})
        count += 1

        # Firestore batch limit is 500
        if count % 500 == 0:
            batch.commit()
            batch = db.batch()

    # commit remaining
    if count % 500 != 0:
        batch.commit()
