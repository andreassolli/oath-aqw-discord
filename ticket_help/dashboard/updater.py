import discord

from config import LEADERBOARD_CHANNEL_ID

from .leaderboard import LeaderboardView, build_leaderboard_embed


async def update_dashboard(client: discord.Client):
    channel = client.get_channel(LEADERBOARD_CHANNEL_ID)

    if not channel:
        print("❌ Leaderboard channel not found.")
        return

    view = LeaderboardView(channel.guild)

    async for msg in channel.history(limit=10):
        if msg.author == client.user:
            await msg.edit(view=view)
            return

    await channel.send(view=view)
