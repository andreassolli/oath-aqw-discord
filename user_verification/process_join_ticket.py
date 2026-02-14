import asyncio

import discord

from config import TICKET_LOG_CHANNEL_ID
from firebase_client import db

from .embed_join_log import build_join_log_embed
from .utils import change_roles, fetch_aqw_profile


async def process_join_ticket(
    *,
    interaction: discord.Interaction,
    discord_id: int,
    ign: str,
    status: str,  # "approved" or "declined"
):
    guild = interaction.guild
    if guild is None:
        return

    channel = interaction.channel
    if not isinstance(channel, discord.TextChannel):
        return

    if status == "approved":
        profile = await fetch_aqw_profile(ign)
        ccid = profile["ccid"]
        guild_name = profile["guild"]

        if guild_name.lower() != "oath":
            await interaction.followup.send(
                f"❌ Character is not in Oath (current: {guild_name})",
                ephemeral=True,
            )
            return

        member = guild.get_member(discord_id)
        if member:
            await member.edit(nick=ign)
            await change_roles(member, is_join_event=True)

        db.collection("users").document(str(discord_id)).set(
            {
                "aqw_username": ign,
                "ccid": ccid,
                "guild": guild_name,
                "verified": True,
                "verified_at": discord.utils.utcnow(),
            },
            merge=True,
        )

    # 🔥 Logging
    log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)

    if isinstance(log_channel, discord.TextChannel):
        embed = build_join_log_embed(
            guild=guild,
            discord_id=discord_id,
            ign=ign,
            handled_by_id=interaction.user.id,
            status=status,
        )
        await log_channel.send(embed=embed)

    # Cleanup
    db.collection("join_tickets").document(str(channel.id)).delete()

    await interaction.followup.send(
        f"Join request {status}. Channel closing in 10 seconds.",
        ephemeral=True,
    )

    await asyncio.sleep(10)
    await channel.delete()
