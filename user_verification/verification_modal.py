from datetime import datetime
from typing import Any, Dict, cast
from urllib.parse import quote

import discord
from google.cloud import firestore

from config import (
    NEW_TICKET_CATEGORY_ID,
    OATHSWORN_ROLE_ID,
    OFFICER_ROLE_ID,
    TEAM_CATEGORY_ID,
    TICKET_LOG_CHANNEL_ID,
)
from firebase_client import db
from update_badges import get_total_badges
from user_profile.utils import (
    calculate_epic_badges,
    calculate_total_badges,
    fetch_badges,
)
from user_verification.close_ticket import CloseTicketView
from user_verification.embed_verify_log import build_verification_log_embed
from user_verification.utils import (
    build_join_ticket_embed,
    change_roles,
    check_for_bot_badges,
    fetch_aqw_profile,
)

from .user_join import DidUserJoinView


class VerificationModal(discord.ui.Modal):
    def __init__(self, action: str):
        super().__init__(title="AQW Verification")
        self.action = action  # "verify" or "join"

        self.username = discord.ui.TextInput(
            label="AQW Username",
            placeholder="Enter your AQW character name",
            required=True,
            max_length=25,
        )

        self.add_item(self.username)

    async def on_submit(self, interaction: discord.Interaction):
        encoded_name = quote(self.username.value, safe="")
        user_id = interaction.user.id

        await interaction.response.defer(ephemeral=True)

        user = await fetch_aqw_profile(encoded_name)
        if not user:
            return await interaction.followup.send(
                f"❌ Could not find AQW profile for username: **{self.username.value}**",
                ephemeral=True,
            )

        if self.action == "verify" or user["guild"] == "Oath":
            user_ref = db.collection("users").document(str(user_id))

            doc = cast(Any, user_ref.get())
            data: Dict[str, Any] = doc.to_dict() or {}

            old_ign: str | None = data.get("aqw_username")
            previous_igns: list[str] = data.get("previous_igns", [])

            updates: dict[str, Any] = {
                "aqw_username": self.username.value,
                "ccid": user["ccid"],
                "guild": user["guild"],
                "verified": True,
                "verified_at": discord.utils.utcnow(),
            }

            if old_ign and old_ign.lower() != self.username.value.lower():
                # Avoid duplicates
                if old_ign not in previous_igns:
                    updates["previous_igns"] = firestore.ArrayUnion([old_ign])

            user_ref.set(updates, merge=True)

            guild = interaction.guild
            if guild is None:
                return await interaction.followup.send(
                    "❌ This interaction is not in a guild.",
                    ephemeral=True,
                )

            log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
            member = guild.get_member(user_id)
            if member:
                await change_roles(
                    member,
                    is_join_event=False,
                    verified_guild=user["guild"],
                )
                await member.edit(nick=self.username.value)

            if isinstance(log_channel, discord.TextChannel):
                embed = build_verification_log_embed(
                    guild=guild,
                    discord_id=user_id,
                    ign=self.username.value,
                    aqw_username=old_ign,
                    previous_igns=previous_igns,
                    guild_name=user.get("guild"),
                )
                await log_channel.send(embed=embed)

            await interaction.followup.send(
                f"✅ **Verification complete**\nAQW Username: **{self.username.value}**\nGuild: **{user.get('guild', 'None')}**",
                ephemeral=True,
            )

        elif self.action == "join":
            guild_obj = interaction.guild
            if guild_obj is None:
                return await interaction.followup.send(
                    "❌ This interaction is not in a guild.",
                    ephemeral=True,
                )

            category = guild_obj.get_channel(NEW_TICKET_CATEGORY_ID)

            if not isinstance(category, discord.CategoryChannel):
                return await interaction.followup.send(
                    "❌ Ticket category not found or is not a category.",
                    ephemeral=True,
                )

            member = interaction.user
            if not isinstance(member, discord.Member):
                return await interaction.followup.send(
                    "❌ This action must be used in a server.",
                    ephemeral=True,
                )

            ccid = user["ccid"]
            level = user["level"]
            badges = await fetch_badges(ccid)
            total_badges = calculate_total_badges(badges)
            epic_badges = calculate_epic_badges(badges)
            bot_badges = check_for_bot_badges(badges)

            query = db.collection("bans").where("ccid", "==", ccid).limit(1).get()
            docs = list(query)
            guild = interaction.guild
            if not guild:
                return await interaction.followup.send(
                    "❌ This action must be used in a server.",
                    ephemeral=True,
                )
            if docs and docs[0].exists:
                ban_data = docs[0].to_dict() or {}
                log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
                if isinstance(log_channel, discord.TextChannel):
                    embed = build_verification_log_embed(
                        guild=guild,
                        discord_id=user_id,
                        ign=self.username.value,
                        aqw_username=self.username.value,
                        previous_igns=[ban_data["username"]]
                        if ban_data.get("username")
                        else [],
                        guild_name=user["guild"] if user["guild"] else "",
                        denied=True,
                    )
                    log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
                    if isinstance(log_channel, discord.TextChannel):
                        await log_channel.send(embed=embed)

                return await interaction.followup.send(
                    "❌ Your application has been rejected.",
                    ephemeral=True,
                )

            channel = await guild_obj.create_text_channel(
                name=f"join-{member.name}",
                category=category,
                topic=f"Join request | IGN: {self.username.value} | Discord: {member.id}",
            )

            # Permissions
            await channel.set_permissions(guild_obj.default_role, view_channel=False)
            await channel.set_permissions(member, view_channel=True, send_messages=True)

            officer_role = guild_obj.get_role(OFFICER_ROLE_ID)
            head_officer_role = guild_obj.get_role(OATHSWORN_ROLE_ID)

            for role in (officer_role, head_officer_role):
                if role:
                    await channel.set_permissions(
                        role, view_channel=True, send_messages=True
                    )

            embed = build_join_ticket_embed(
                guild=guild_obj,
                discord_id=interaction.user.id,
                ign=self.username.value,
            )

            message = await channel.send(
                officer_role.mention if officer_role else "@Officer",
                embed=embed,
                view=DidUserJoinView(
                    discord_id=interaction.user.id,
                    ign=self.username.value,
                ),
            )

            # 🔥 Now store ticket AFTER message exists
            identifier = f"{self.username.value}:{interaction.user.id}"
            db.collection("join_tickets").document(identifier).set(
                {
                    "channel_id": str(channel.id),
                    "message_id": str(message.id),
                    "discord_id": interaction.user.id,
                    "ign": self.username.value,
                    "created_at": datetime.utcnow(),
                    "status": "open",
                    "total_badges": total_badges,
                    "level": level,
                    "epic_badges": epic_badges,
                    "derp_moosefish": bot_badges.get("moosefish"),
                    "you_mad_bro": bot_badges.get("mad_bro"),
                }
            )

            await interaction.followup.send(
                f"✅ Ticket created: {channel.mention}",
                ephemeral=True,
            )
            await interaction.followup.send(
                f"🛡️ **Request to join submitted**\n"
                f"AQW Username: **{self.username.value}**\n\n"
                "An officer will review your request.",
                ephemeral=True,
            )
