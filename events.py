from typing import Literal

import discord

from config import EVENT_CHANNEL_ID, OATH_EVENT_CHANNEL_ID


async def announce_event_winner(
    user: discord.Member,
    title: str,
    message: discord.Message,
    where: Literal["All", "Oath"],
    interaction: discord.Interaction,
):
    channel_id = EVENT_CHANNEL_ID if where == "All" else OATH_EVENT_CHANNEL_ID
    guild = interaction.guild
    if not guild:
        raise RuntimeError("Guild not found")
    channel = guild.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        raise RuntimeError("Event channel is not a text channel")
    embed = discord.Embed(
        title=title,
        description=f"{user.mention} {message.content}",
        color=discord.Color.green(),
    )
    await channel.send(embed=embed)
