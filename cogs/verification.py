from multiprocessing.spawn import old_main_modules
from typing import Any, Dict, cast

import discord
from discord import app_commands
from discord.app_commands.models import app_command_option_factory
from discord.ext import commands
from discord.types.command import ApplicationCommand
from google.cloud import firestore
from google.cloud.firestore import DocumentSnapshot

from config import DISCORD_MANAGER_ROLE_ID, OATHSWORN_ROLE_ID
from firebase_client import db
from user_verification.process_join_ticket import process_join_ticket
from user_verification.utils import fetch_aqw_profile
from user_verification.verification_panel import setup_verification_panel
from utils import is_bot_channel


class VerificationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        await setup_verification_panel(self.bot)

    @app_commands.command(
        name="list-guild-members",
        description="List all verified members in a specific guild",
    )
    @app_commands.describe(guild="The name of the guild to list members for")
    @is_bot_channel()
    async def list_guild_members(self, interaction: discord.Interaction, guild: str):
        await interaction.response.defer(ephemeral=True)

        users_ref = db.collection("users")
        docs = (
            users_ref.where("verified", "==", True).where("guild", "==", guild).stream()
        )

        members = []
        for doc in docs:
            data = doc.to_dict()
            aqw_username = data.get("aqw_username", "Unknown")
            discord_id = data.get("discord_id")
            if discord_id:
                members.append(f"{aqw_username} (ID: {discord_id})")

        if not members:
            return await interaction.followup.send(
                f"No verified members found in guild **{guild}**.", ephemeral=True
            )

        message = f"**Verified Members in {guild}:**\n" + "\n".join(members)
        await interaction.followup.send(message, ephemeral=True)

    @app_commands.command(
        name="list-guilds", description="List all verified guilds in the server"
    )
    @is_bot_channel()
    async def list_guilds(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        users_ref = db.collection("users")
        docs = users_ref.where("verified", "==", True).stream()

        guild_counts: Dict[str, int] = {}
        for doc in docs:
            data = doc.to_dict()
            guild = data.get("guild", "Unknown")
            guild_counts[guild] = guild_counts.get(guild, 0) + 1

        if not guild_counts:
            return await interaction.followup.send(
                "No verified users found.", ephemeral=True
            )

        sorted_guilds = sorted(guild_counts.items(), key=lambda x: x[1], reverse=True)
        message = "**Verified Guilds:**\n"
        for guild, count in sorted_guilds:
            message += f"- {guild}: {count} members\n"

        await interaction.followup.send(message, ephemeral=True)

    @app_commands.command(
        name="sync-nicknames", description="Sync nicknames for all verified users"
    )
    @app_commands.checks.has_role(DISCORD_MANAGER_ROLE_ID)
    async def sync_nicknames(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        users_ref = db.collection("users")
        docs = users_ref.where("verified", "==", True).stream()

        updated_count = 0
        for doc in docs:
            data = doc.to_dict()
            discord_id = data.get("discord_id")
            aqw_username = data.get("aqw_username")

            if not discord_id or not aqw_username:
                continue

            guild = interaction.guild
            if not guild:
                continue

            member = guild.get_member(int(discord_id))
            if not member:
                continue

            try:
                await member.edit(nick=aqw_username)
                updated_count += 1
            except Exception as e:
                print(f"Failed to update nickname for {member}: {e}")

        await interaction.followup.send(
            f"✅ Synced nicknames for {updated_count} verified users.",
            ephemeral=True,
        )

    @app_commands.command(
        name="approve-join", description="Approve a user's join request"
    )
    @app_commands.describe(
        user="The Discord user to approve", username="Their AQW username"
    )
    @app_commands.checks.has_role(OATHSWORN_ROLE_ID)
    async def join_approve(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        username: str,
    ):

        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send(
                "❌ Must be used inside a join ticket channel.",
                ephemeral=True,
            )

        identifier = f"{username}:{user}"
        doc = db.collection("join_tickets").document(identifier).get()

        if not doc.exists:
            return await interaction.followup.send(
                "❌ No join ticket found for this channel.",
                ephemeral=True,
            )

        data = doc.to_dict()

        if not data:
            return await interaction.followup.send(
                "❌ Join ticket data is missing.",
                ephemeral=True,
            )

        await process_join_ticket(
            interaction=interaction,
            discord_id=data["discord_id"],
            ign=data["ign"],
            status="approved",
        )

    @app_commands.command(
        name="reject-join", description="Reject a user's join request"
    )
    @app_commands.describe(
        user="The Discord user to reject", username="Their AQW username"
    )
    @app_commands.checks.has_role(OATHSWORN_ROLE_ID)
    async def join_reject(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        username: str,
    ):
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send(
                "❌ Must be used inside a join ticket channel.",
                ephemeral=True,
            )

        identifier = f"{username}_{user}"
        doc = db.collection("join_tickets").document(identifier).get()

        if not doc.exists:
            return await interaction.followup.send(
                "❌ No join ticket found for this channel.",
                ephemeral=True,
            )

        data = doc.to_dict()

        if not data:
            return await interaction.followup.send(
                "❌ Join ticket data is missing.",
                ephemeral=True,
            )

        await process_join_ticket(
            interaction=interaction,
            discord_id=data["discord_id"],
            ign=data["ign"],
            status="rejected",
        )

    @app_commands.command(name="force-verify", description="Force verify a user")
    @app_commands.describe(
        user="The Discord user to verify", username="Their AQW username"
    )
    @app_commands.checks.has_role(DISCORD_MANAGER_ROLE_ID)
    async def force_verify(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        username: str,
    ):
        await interaction.response.defer(ephemeral=True)

        aqw_username = username.strip()

        profile = await fetch_aqw_profile(aqw_username)
        if not profile:
            return await interaction.followup.send(
                f"❌ Could not find AQW profile for **{aqw_username}**",
                ephemeral=True,
            )

        user_ref = db.collection("users").document(str(user.id))
        doc = cast(DocumentSnapshot, user_ref.get())
        data: Dict[str, Any] = doc.to_dict() or {}

        old_ign: str | None = data.get("aqw_username")
        previous_igns: list[str] = data.get("previous_igns", [])

        updates: dict[str, Any] = {
            "aqw_username": aqw_username,
            "ccid": profile["ccid"],
            "guild": profile["guild"],
            "verified": True,
            "verified_at": discord.utils.utcnow(),
        }

        if old_ign and old_ign != aqw_username:
            if old_ign not in previous_igns:
                updates["previous_igns"] = firestore.ArrayUnion([old_ign])

        user_ref.set(updates, merge=True)

        await interaction.followup.send(
            f"✅ **Force verification complete**\n"
            f"User: {user.mention}\n"
            f"AQW Username: **{aqw_username}**\n"
            f"Guild: **{profile.get('guild', 'None')}**",
            ephemeral=True,
        )


# ✅ MUST be at file level
async def setup(bot: commands.Bot):
    await bot.add_cog(VerificationCog(bot))
