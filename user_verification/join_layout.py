import asyncio
from typing import Any, Dict, cast
from urllib.parse import quote

import discord
from google.cloud import firestore

from config import OATHSWORN_ROLE_ID, TICKET_LOG_CHANNEL_ID
from firebase_client import db
from user_verification.embed_join_log import build_join_log_embed
from user_verification.utils import change_roles, fetch_aqw_profile


class JoinLayoutView(discord.ui.LayoutView):
    def __init__(self, username: str, discord_id: int):
        super().__init__(timeout=None)
        self.ign = username
        self.discord_id = discord_id

        self.container1 = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"<:hands:1505158458494681138> **{username} wants to join the guild!**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"<:star:1503523567898460311> View more details about {username}"
                ),
                accessory=DetailsButton(),
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content="Invite them to the guild! Approve upon joining."
                ),
                accessory=JoinedButton(),
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content="Did the user change their mind or break any rules?"
                ),
                accessory=NoJoinButton(),
            ),
            accent_colour=discord.Colour(7344907),
        )

        self.add_item(self.container1)


class JoinedButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="✅ Approve",
            style=discord.ButtonStyle.green,
            custom_id="join_ticket_yes",
        )
        return

    async def callback(self, interaction: discord.Interaction):
        layout: JoinLayoutView = self.view
        await interaction.response.defer()
        ticket_channel = interaction.channel
        encoded_name = quote(layout.ign, safe="")
        if not isinstance(ticket_channel, discord.TextChannel):
            return await interaction.followup.send(
                "❌ This action must be used inside a ticket channel.",
                ephemeral=True,
            )
        profile = await fetch_aqw_profile(encoded_name)
        if profile is None:
            return await interaction.followup.send(
                "❌ Could not find a profile for that username.",
                ephemeral=True,
            )
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

        member = guild_obj.get_member(layout.discord_id)

        if member is not None:
            await member.edit(nick=layout.ign)

        user_ref = db.collection("users").document(str(layout.discord_id))

        doc = cast(Any, user_ref.get())
        data: Dict[str, Any] = doc.to_dict() or {}

        old_ign: str | None = data.get("aqw_username")
        previous_igns: list[str] = data.get("previous_igns", [])

        updates: dict[str, Any] = {
            "aqw_username": layout.ign,
            "aqw_username_lower": layout.ign.lower(),
            "ccid": ccid,
            "guild": guild,
            "verified": True,
            "verified_at": discord.utils.utcnow(),
        }

        if old_ign and old_ign.lower() != layout.ign.lower():
            # Avoid duplicates
            if old_ign not in previous_igns:
                updates["previous_igns"] = firestore.ArrayUnion([old_ign])

        user_ref.set(updates, merge=True)
        channel_id = ticket_channel.id

        doc_ref = db.collection("join_tickets").document(
            f"{layout.ign}:{layout.discord_id}"
        )
        doc = doc_ref.get()

        if doc.exists:
            doc_ref.delete()

        guild = interaction.guild
        if guild is None:
            return

        channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        member = guild.get_member(layout.discord_id)
        if member:
            await change_roles(
                member,
                is_join_event=True,
            )
            await member.edit(nick=layout.ign)

        if not isinstance(channel, discord.TextChannel):
            return

        embed = build_join_log_embed(
            guild=guild,
            discord_id=layout.discord_id,
            ign=layout.ign,
            handled_by_id=interaction.user.id,
            status="approved",
        )

        await channel.send(embed=embed)

        await interaction.followup.send(
            f"✅ **Verification complete** for **{layout.ign}**.\n"
            "This ticket will close in 10 seconds."
        )

        await asyncio.sleep(10)

        await ticket_channel.delete()


class DetailsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="🔍 Details",
            style=discord.ButtonStyle.blurple,
            custom_id="join_ticket_details",
        )

    async def callback(self, interaction: discord.Interaction):
        layout: JoinLayoutView = self.view
        channel_id = str(interaction.channel_id)

        doc_ref = db.collection("join_tickets").document(
            f"{layout.ign}:{layout.discord_id}"
        )
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.response.send_message(
                "❌ This button can only be used inside a ticket.",
                ephemeral=True,
            )

        ticket = doc.to_dict()

        if not ticket:
            return await interaction.response.send_message(
                "❌ This ticket does not exist.",
                ephemeral=True,
            )

        embed = discord.Embed(
            title="Join Ticket Info",
            color=discord.Color.blurple(),
        )

        moosefish = "✅" if ticket["derp_moosefish"] else "❌"
        you_mad_bro = "✅" if ticket["you_mad_bro"] else "❌"
        touch_mass = "✅" if ticket["touch_mass"] else "❌"
        martial_artist = "✅" if ticket["martial_artist"] else "❌"

        embed.add_field(name="IGN", value=ticket["ign"], inline=True)
        embed.add_field(name="Level", value=ticket["level"], inline=True)

        embed.add_field(name="Total Badges", value=ticket["total_badges"], inline=True)
        embed.add_field(name="Epic", value=ticket["epic_badges"], inline=True)

        embed.add_field(name="Moosefish", value=moosefish, inline=True)
        embed.add_field(name="You Mad Bro", value=you_mad_bro, inline=True)

        embed.add_field(name="Touch Mass", value=touch_mass, inline=True)
        embed.add_field(name="Martial Artist", value=martial_artist, inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)


class NoJoinButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="❌ Deny",
            style=discord.ButtonStyle.red,
            custom_id="join_ticket_no",
        )

    async def callback(self, interaction: discord.Interaction):
        layout: JoinLayoutView = self.view
        await interaction.response.defer()
        ticket_channel = interaction.channel
        if not isinstance(ticket_channel, discord.TextChannel):
            return await interaction.followup.send(
                "❌ This action must be used inside a ticket channel.",
                ephemeral=True,
            )

        channel_id = ticket_channel.id

        doc_ref = db.collection("join_tickets").document(
            f"{layout.ign}:{layout.discord_id}"
        )
        doc = doc_ref.get()

        if doc.exists:
            doc_ref.delete()

        guild = interaction.guild
        if guild is None:
            return

        channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)

        if not isinstance(channel, discord.TextChannel):
            return

        embed = build_join_log_embed(
            guild=guild,
            discord_id=layout.discord_id,
            ign=layout.ign,
            handled_by_id=interaction.user.id,
            status="declined",
        )

        await channel.send(embed=embed)

        await interaction.followup.send(
            "❌ Join request declined. Ticket will be deleted in 10 seconds."
        )

        await asyncio.sleep(10)

        await ticket_channel.delete()
