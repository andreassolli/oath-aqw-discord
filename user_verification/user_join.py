import asyncio
from typing import Any, Dict, cast

import discord
from google.cloud import firestore

from config import TICKET_LOG_CHANNEL_ID
from firebase_client import db
from user_verification.embed_join_log import build_join_log_embed
from user_verification.utils import change_roles, fetch_aqw_profile


class DidUserJoinView(discord.ui.View):
    def __init__(self, discord_id: int, ign: str):
        super().__init__(timeout=None)
        self.discord_id = discord_id
        self.ign = ign

    @discord.ui.button(
        label="Yes - User Joined",
        style=discord.ButtonStyle.green,
        custom_id="join_ticket_yes",
    )
    async def yes(self, interaction: discord.Interaction, _):
        await interaction.response.defer()
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send(
                "❌ This action must be used inside a ticket channel.",
                ephemeral=True,
            )
        profile = await fetch_aqw_profile(self.ign)
        ccid = profile["ccid"]
        guild = profile["guild"]

        if guild.lower() != "oath":
            return await interaction.followup.send(
                f"❌ Character is not in Oath (current: {guild})",
                ephemeral=True,
            )

        guild_obj = interaction.guild
        if guild_obj is None:
            return await interaction.followup.send(
                "❌ This interaction is not in a guild.",
                ephemeral=True,
            )

        member = guild_obj.get_member(self.discord_id)

        if member is not None:
            await member.edit(nick=self.ign)

        user_ref = db.collection("users").document(str(self.discord_id))

        doc = cast(Any, user_ref.get())
        data: Dict[str, Any] = doc.to_dict() or {}

        old_ign: str | None = data.get("aqw_username")
        previous_igns: list[str] = data.get("previous_igns", [])

        updates: dict[str, Any] = {
            "aqw_username": self.ign,
            "ccid": ccid,
            "guild": guild,
            "verified": True,
            "verified_at": discord.utils.utcnow(),
        }

        if old_ign and old_ign.lower() != self.ign.lower():
            # Avoid duplicates
            if old_ign not in previous_igns:
                updates["previous_igns"] = firestore.ArrayUnion([old_ign])

        user_ref.set(updates, merge=True)
        db.collection("join_tickets").document(str(channel.id)).delete()

        guild = interaction.guild
        if guild is None:
            return

        channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        member = guild.get_member(self.discord_id)
        if member:
            await change_roles(
                member,
                is_join_event=True,
            )

        if not isinstance(channel, discord.TextChannel):
            return

        embed = build_join_log_embed(
            guild=guild,
            discord_id=self.discord_id,
            ign=self.ign,
            handled_by_id=interaction.user.id,
            status="approved",
        )

        await channel.send(embed=embed)

        await interaction.followup.send(
            f"✅ **Verification complete** for **{self.ign}**.\n"
            "This ticket will close in 10 seconds."
        )

        await asyncio.sleep(10)
        channel = interaction.channel
        if isinstance(channel, discord.TextChannel):
            await channel.delete()

    @discord.ui.button(
        label="No - User Did Not Join",
        style=discord.ButtonStyle.red,
        custom_id="join_ticket_no",
    )
    async def no(self, interaction: discord.Interaction, _):
        await interaction.response.defer()
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send(
                "❌ This action must be used inside a ticket channel.",
                ephemeral=True,
            )

        db.collection("join_tickets").document(str(channel.id)).delete()

        guild = interaction.guild
        if guild is None:
            return

        channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)

        if not isinstance(channel, discord.TextChannel):
            return

        embed = build_join_log_embed(
            guild=guild,
            discord_id=self.discord_id,
            ign=self.ign,
            handled_by_id=interaction.user.id,
            status="declined",
        )

        await channel.send(embed=embed)

        await interaction.followup.send(
            "❌ Join request declined. Ticket will be deleted in 10 seconds."
        )

        await asyncio.sleep(10)

        if isinstance(channel, discord.TextChannel):
            await channel.delete()
