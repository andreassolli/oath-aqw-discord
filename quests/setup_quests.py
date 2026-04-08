import discord

from config import EVENT_CHANNEL_ID
from quests.panel import build_static_quest_embed
from quests.view import QuestView


async def setup_quests(client: discord.Client):
    channel = client.get_channel(EVENT_CHANNEL_ID)

    if not channel:
        try:
            channel = await client.fetch_channel(EVENT_CHANNEL_ID)
        except Exception as e:
            print(f"❌ Failed to fetch channel: {e}")
            return

    embed = await build_static_quest_embed()

    async for msg in channel.history(limit=10):
        if (
            msg.author == client.user
            and msg.embeds
            and msg.embeds[0].title == "📜 Available Quests"
        ):
            await msg.delete()
            await channel.send(embed=embed, view=QuestView())
            return

    await channel.send(embed=embed, view=QuestView())
