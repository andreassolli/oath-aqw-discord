import asyncio
from typing import Any, Dict, cast
from urllib.parse import quote

import discord
from discord import app_commands
from discord.ext import commands
from google.cloud import firestore
from google.cloud.firestore import DocumentSnapshot

from config import (
    DISCORD_MANAGER_ROLE_ID,
    INITIATE_ROLE_ID,
    OATHSWORN_ROLE_ID,
    STRANGER_ROLE_ID,
    UNSWORN_ROLE_ID,
)
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
        docs = users_ref.where("verified", "==", True).stream()

        guild_lower = guild.lower()

        filtered_docs = [
            doc for doc in docs if doc.to_dict().get("guild", "").lower() == guild_lower
        ]

        members = []
        for doc in filtered_docs:
            data = doc.to_dict()
            aqw_username = data.get("aqw_username", "Unknown")
            discord_id = doc.id
            if discord_id:
                members.append(f"{aqw_username}")

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
            guild = data.get("guild", "")
            if guild != "":
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
            discord_id = doc.id
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

    @app_commands.command(
        name="mass-verify",
        description="Force verify all users based on their nicknames",
    )
    @app_commands.checks.has_role(DISCORD_MANAGER_ROLE_ID)
    async def mass_verify(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            return await interaction.followup.send(
                "❌ This command can only be used within a server.",
                ephemeral=True,
            )
        initiate_role = guild.get_role(INITIATE_ROLE_ID)
        unsworn_role = guild.get_role(UNSWORN_ROLE_ID)
        stranger_role = guild.get_role(STRANGER_ROLE_ID)

        if not guild:
            return await interaction.followup.send(
                "❌ This command can only be used within a server.",
                ephemeral=True,
            )

        members = guild.members
        verified_count = 0
        failed_count = 0
        failed_members = []
        roles_to_check = {INITIATE_ROLE_ID, UNSWORN_ROLE_ID}
        sleep = 2

        async def handle_failed_verification(member: discord.Member):
            roles_to_remove = []

            if initiate_role and initiate_role in member.roles:
                roles_to_remove.append(initiate_role)

            if unsworn_role and unsworn_role in member.roles:
                roles_to_remove.append(unsworn_role)

            try:
                if roles_to_remove:
                    await member.remove_roles(
                        *roles_to_remove, reason="Failed AQW verification"
                    )

                if stranger_role and stranger_role not in member.roles:
                    await member.add_roles(
                        stranger_role, reason="Failed AQW verification"
                    )

            except discord.Forbidden:
                print(f"Missing permissions to modify roles for {member}")
            except Exception as e:
                print(f"Error modifying roles for {member}: {e}")

        for member in members:
            if member.bot:
                continue
            member_role_ids = {role.id for role in member.roles}

            if not member_role_ids.intersection(roles_to_check):
                continue

            original_name = member.nick or member.name
            encoded_name = quote(original_name, safe="")
            print(f"Attempting to verify {original_name}")
            try:
                profile = await fetch_aqw_profile(encoded_name)
                await asyncio.sleep(sleep)
            except ValueError:
                print(f"ValueError while verifying {original_name}")
                await handle_failed_verification(member)
                print(
                    f"Removing roles from {original_name} due to verification failure"
                )
                failed_count += 1
                failed_members.append(original_name)
                await asyncio.sleep(sleep)
                continue
            except Exception as e:
                print(f"Unexpected error verifying {original_name}: {e}")
                await handle_failed_verification(member)
                print(
                    f"Removing roles from {original_name} due to verification failure"
                )
                failed_count += 1
                failed_members.append(original_name)
                await asyncio.sleep(sleep)
                continue

            if profile:
                user_ref = db.collection("users").document(str(member.id))
                user_ref.set(
                    {
                        "aqw_username": original_name,
                        "ccid": profile["ccid"],
                        "guild": profile["guild"],
                        "verified": True,
                        "verified_at": discord.utils.utcnow(),
                    },
                    merge=True,
                )
                verified_count += 1
            else:
                print(f"Could not verify {original_name}")
                await handle_failed_verification(member)

                print(
                    f"Removing roles from {original_name} due to verification failure"
                )

                failed_count += 1
                failed_members.append(original_name)
                await asyncio.sleep(sleep)

        await interaction.followup.send(
            f"✅ Mass verification complete.\n"
            f"Verified: {verified_count} users\n"
            f"Failed: {failed_count} users (no matching AQW profile found)",
            ephemeral=True,
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
