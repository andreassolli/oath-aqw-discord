import discord

from config import LEADERBOARD_CHANNEL_ID

from .leaderboard import build_leaderboard_embed


async def update_dashboard(client: discord.Client):
    channel = client.get_channel(LEADERBOARD_CHANNEL_ID)

    if not channel:
        print("❌ Leaderboard channel not found.")
        return

    embed = await build_leaderboard_embed(channel.guild)

    async for msg in channel.history(limit=10):
        if msg.author == client.user and msg.embeds:
            await msg.edit(embed=embed)
            return

    await channel.send(embed=embed)
