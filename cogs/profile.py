from typing import Any, Dict, List, Optional, cast

import discord
from discord import app_commands
from discord.ext import commands
from google.cloud.firestore import DocumentSnapshot

from config import ALLOWED_COMMANDS_CHANNELS, DISCORD_MANAGER_ROLE_ID
from firebase_client import db
from user_profile.badge_panel import setup_verification_panel
from user_profile.image_generation import generate_profile_card
from user_profile.profile_view import ProfileView

MANUAL_BADGES = [
    "Forge",
    "Forge+",
    "Guild Founder",
]


class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def badge_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=badge, value=badge)
            for badge in MANUAL_BADGES
            if current.lower() in badge.lower()
        ]

    @app_commands.command(
        name="profile",
        description="Show your profile card or another user's profile",
    )
    @app_commands.describe(user="User whose profile you want to view")
    async def profile(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None,
    ):
        # Slash commands should always be deferred if we do work
        await interaction.response.defer(thinking=True)

        # Slash commands only make sense in guilds for profiles
        if interaction.guild is None:
            await interaction.followup.send(
                "❌ Profiles can only be viewed inside a server.",
                ephemeral=True,
            )
            return

        if interaction.channel_id not in ALLOWED_COMMANDS_CHANNELS:
            allowed_mentions = ", ".join(
                f"<#{cid}>" for cid in ALLOWED_COMMANDS_CHANNELS
            )

            await interaction.followup.send(
                f"❌ This command can only be used in {allowed_mentions}.",
                ephemeral=True,
            )
            return

        # Default to the command author
        target = user or interaction.user

        # 🔒 Ensure target is a Member (not User)
        if not isinstance(target, discord.Member):
            member = interaction.guild.get_member(target.id)
            if member is None:
                await interaction.followup.send(
                    "❌ That user is not a member of this server.",
                    ephemeral=True,
                )
                return
        else:
            member = target

        try:
            image_buffer, badges = await generate_profile_card(
                interaction,
                target=member,
            )

            await interaction.followup.send(
                file=discord.File(image_buffer, filename="profile.png"),
                view=ProfileView(badges),
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Error generating profile:\n```{e}```",
                ephemeral=True,
            )
            raise  # keep traceback in logs

    @app_commands.command(
        name="grant-badge",
        description="Grant a badge to a user (admin only)",
    )
    @app_commands.describe(
        user="User you want to grant the badge to",
        badge="Badge name to grant",
    )
    @app_commands.autocomplete(badge=badge_autocomplete)
    @app_commands.checks.has_role(DISCORD_MANAGER_ROLE_ID)
    async def grant_badge(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        badge: str,
    ):
        await interaction.response.defer(ephemeral=True)

        if interaction.guild is None:
            return await interaction.followup.send(
                "❌ This command must be used in a server.",
                ephemeral=True,
            )

        if interaction.channel_id not in ALLOWED_COMMANDS_CHANNELS:
            allowed_mentions = ", ".join(
                f"<#{cid}>" for cid in ALLOWED_COMMANDS_CHANNELS
            )
            return await interaction.followup.send(
                f"❌ This command can only be used in {allowed_mentions}.",
                ephemeral=True,
            )

        if badge not in MANUAL_BADGES:
            return await interaction.followup.send(
                "❌ Invalid badge.",
                ephemeral=True,
            )

        user_ref = db.collection("users").document(str(user.id))
        doc = cast(DocumentSnapshot, user_ref.get())
        data: Dict[str, Any] = doc.to_dict() or {}

        current_badges: list[str] = data.get("badges", [])

        if badge not in current_badges:
            current_badges.append(badge)

        user_ref.set({"badges": current_badges}, merge=True)

        await interaction.followup.send(
            f"✅ Granted **{badge}** to {user.mention}",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))

    async def post_panel():
        await bot.wait_until_ready()
        await setup_verification_panel(bot)

    bot.loop.create_task(post_panel())
