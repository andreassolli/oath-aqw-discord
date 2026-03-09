import asyncio

import discord

from config import TICKET_LOG_CHANNEL_ID
from firebase_client import db

from .embed_join_log import build_join_log_embed
from .utils import change_roles, fetch_aqw_profile


async def process_join_ticket(
    *,
    interaction: discord.Interaction,
    status: str,
):

    guild = interaction.guild
    channel = interaction.channel

    if guild is None or not isinstance(channel, discord.TextChannel):
        return

    #
    # FETCH TICKET USING CHANNEL ID
    #
    ticket_query = (
        db.collection("join_tickets")
        .where("channel_id", "==", channel.id)
        .limit(1)
        .stream()
    )

    ticket_doc = next(ticket_query, None)

    if ticket_doc is None:
        await interaction.followup.send(
            "❌ No join ticket found for this channel.",
            ephemeral=True,
        )
        return

    ticket = ticket_doc.to_dict()

    discord_id = ticket["discord_id"]
    ign = ticket["ign"]

    #
    # APPROVAL LOGIC
    #
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

    #
    # LOG ACTION
    #
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

    #
    # DELETE FIRESTORE TICKET
    #
    ticket_doc.reference.delete()

    #
    # USER FEEDBACK
    #
    await interaction.followup.send(
        f"Join request {status}. Channel closing in 10 seconds.",
        ephemeral=True,
    )

    #
    # DELETE CHANNEL
    #
    await asyncio.sleep(10)

    try:
        await channel.delete(reason=f"Join request {status}")
    except discord.Forbidden:
        await interaction.followup.send(
            "⚠️ Missing permission to delete ticket channel.",
            ephemeral=True,
        )
