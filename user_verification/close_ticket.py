from typing import cast

import discord
from google.cloud.firestore import DocumentSnapshot

from config import OATHSWORN_ROLE_ID, OFFICER_ROLE_ID
from firebase_client import db
from user_verification.user_join import DidUserJoinView


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.blurple,
        custom_id="join_close_ticket",
    )
    async def close_ticket(self, interaction: discord.Interaction, _):

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return await interaction.response.send_message(
                "❌ This action must be used inside a ticket channel.",
                ephemeral=True,
            )

        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message(
                "❌ This action must be used in a server.",
                ephemeral=True,
            )
        officer_role = guild.get_role(OFFICER_ROLE_ID)
        head_officer_role = guild.get_role(OATHSWORN_ROLE_ID)
        member = interaction.user
        if not isinstance(member, discord.Member):
            return await interaction.followup.send(
                "❌ This action must be used in a server.",
                ephemeral=True,
            )

        if not any(
            role is not None and role in member.roles
            for role in (officer_role, head_officer_role)
        ):
            return await interaction.response.send_message(
                "❌ Only officers can close tickets.",
                ephemeral=True,
            )

        doc = cast(
            DocumentSnapshot,
            db.collection("join_tickets").document(str(channel.id)).get(),
        )

        if not doc.exists:
            return await interaction.response.send_message(
                "❌ Ticket data not found.",
                ephemeral=True,
            )

        data = doc.to_dict() or {}
        discord_id = data.get("discord_id")
        ign = data.get("ign")

        if not isinstance(discord_id, int) or not isinstance(ign, str):
            return await interaction.response.send_message(
                "❌ Ticket data is corrupted or incomplete.",
                ephemeral=True,
            )

        member_display = member.mention if member else f"`{discord_id}`"

        embed = discord.Embed(
            title="📋 Did the user join the guild?",
            description=f"**User:** {member_display}\n**IGN:** {ign}",
            color=discord.Color.orange(),
        )

        await interaction.response.send_message(
            embed=embed,
            view=DidUserJoinView(discord_id, ign),
        )
