import discord

from config import LEADERBOARD_CHANNEL_ID

from .leaderboard import LeaderboardView, build_leaderboard_embed


async def update_dashboard(client: discord.Client):
    channel = client.get_channel(LEADERBOARD_CHANNEL_ID)

    if not channel:
        print("❌ Leaderboard channel not found.")
        return

    view = LeaderboardView(channel.guild)

    message = await channel.fetch_message(1465382095714259045)
    await message.edit(view=view)
    return
