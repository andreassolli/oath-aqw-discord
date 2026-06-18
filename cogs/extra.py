import math
from datetime import datetime, timedelta, timezone
from typing import Literal

import discord
from discord import app_commands
from discord.abc import Messageable
from discord.ext import commands
from google.cloud import firestore
from google.cloud import firestore as gc_firestore
from google.cloud.firestore import ArrayUnion

from config import (
    ADMIN_ROLE_ID,
    ALLOWED_COMMANDS_CHANNELS,
    BETA_TESTER_ROLE_ID,
    BETA_TESTING_CHANNEL_ID,
    BOT_GUY_ROLE_ID,
    DAGE_CERTIFICATE_ID,
    DARKON_CERTIFICATE_ID,
    DISCORD_MANAGER_ROLE_ID,
    DRAGO_CERTIFICATE_ID,
    DRAKATH_CERTIFICATE_ID,
    EXPERIENCED_HELPER_ROLE_ID,
    GRAMIEL_CERTIFICATE_ID,
    HELPER_CHANNEL_ID,
    INITIATE_ROLE_ID,
    LFG_LOL_ID,
    NULGATH_CERTIFICATE_ID,
    OATHSWORN_ROLE_ID,
    SPEAKER_CERTIFICATE_ID,
    TICKET_INSPECTOR_ROLE_ID,
    TICKET_INSPECTORS_CHANNEL_ID,
    TICKET_LOG_CHANNEL_ID,
    TRANSCENDED_ROLE_ID,
    UNSWORN_ROLE_ID,
)
from economy.gamba.coinflip import run_coinflip
from economy.gamba.doom_view import DoomSpinView
from economy.gamba.utils import has_spun_today
from economy.gamba.yanken_accept_view import RPSAcceptView
from extra_commands.league_team_view import TeamView
from extra_commands.league_teams_embed import LeagueTeamsLayout
from extra_commands.lfg_players import LFGPlayersLayout
from extra_commands.memes import (
    m_bigrig,
    m_dryage,
    m_glad,
    m_gld,
    m_goon_greed,
    m_juns,
    m_mapril,
    m_oath,
    m_og_pro,
    m_og_san,
    m_rcs,
    m_sker,
    m_yokai,
)
from extra_commands.record_holder import record_holder
from extra_commands.record_view import LeaderboardView
from extra_commands.render import render_png
from extra_commands.utils import (
    check_missing_badges,
    count_messages,
    elect_potw,
    format_duration,
    get_user_team,
    has_any_role,
    is_oath_or_allowed_user,
    manual_leaderboard_post,
    send_winner_embed,
    update_message_counts,
)
from extra_commands.wordle import (
    ShareWordleView,
    choose_new_word,
    get_wordle_word,
    guess_word,
)
from extra_commands.wordle_image import generate_wordle_board
from firebase_client import db
from panels.staff_panel import (
    EndLayout,
    ExLayout,
    LeadLayout,
    OfficerLayout,
    StaffLayout,
)
from ticket_help.tickets.points import get_boss_room
from ticket_help.utils.experienced import StartView
from ticket_help.utils.gif_claim import gif_claim
from user_profile.utils import fetch_inventory
from user_verification.layout import TestLayout
from user_verification.utils import change_roles

BOSS_TO_CERTIFICATE = {
    "Champion Drakath": DRAKATH_CERTIFICATE_ID,
    "Ultra Dage": DAGE_CERTIFICATE_ID,
    "Ultra Drago": DRAGO_CERTIFICATE_ID,
    "Ultra Darkon": DARKON_CERTIFICATE_ID,
    "Ultra Speaker": SPEAKER_CERTIFICATE_ID,
    "Ultra Gramiel": GRAMIEL_CERTIFICATE_ID,
    "Ultra Nulgath": NULGATH_CERTIFICATE_ID,
}

STATUS_TO_EMOJI = {
    "Awaiting Trial": "⏳",
    "Under review": "🔍",
    "Rejected": "❌",
    "Passed Trial": "✅",
    "Approved": "✅",
}


class Extra(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="badge-check", description="Check missing badges")
    async def badge_check(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ):
        await interaction.response.defer()
        if interaction.channel_id not in ALLOWED_COMMANDS_CHANNELS:
            allowed_mentions = ", ".join(
                f"<#{cid}>" for cid in ALLOWED_COMMANDS_CHANNELS
            )

            await interaction.followup.send(
                f"❌ This command can only be used in {allowed_mentions}.",
                ephemeral=True,
            )
            return
        guild = interaction.guild
        if not guild:
            await interaction.followup.send(
                f"❌ Guild not found.",
                ephemeral=True,
            )
            return
        member = user if user else guild.get_member(interaction.user.id)
        if not member:
            await interaction.followup.send(
                f"❌ User not found.",
                ephemeral=True,
            )
            return
        embed = await check_missing_badges(member)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="og-san")
    async def og_san(self, interaction: discord.Interaction):
        await m_og_san(interaction)

    @app_commands.command(name="juns")
    async def juns(self, interaction: discord.Interaction):
        await m_juns(interaction)

    @app_commands.command(name="elect-potw", description="Elect a player for POTW")
    @app_commands.checks.has_role(DISCORD_MANAGER_ROLE_ID)
    async def elect_potw(
        self, interaction: discord.Interaction, player: discord.Member
    ):
        await elect_potw(player)
        await interaction.response.send_message(
            f"🎉 {player.mention} has been elected POTW!"
        )

    @app_commands.command(name="nominate", description="Nominate a player for POTW")
    @app_commands.checks.has_any_role(OATHSWORN_ROLE_ID, TRANSCENDED_ROLE_ID)
    async def nominate(self, interaction: discord.Interaction, player: discord.Member):
        is_oath_member = any(role.id == INITIATE_ROLE_ID for role in player.roles)
        if not is_oath_member:
            await interaction.response.send_message(
                f"{player.mention} is not in Oath Guild and cannot be nominated for POTW."
            )
            return

        db.collection("meta").document("potw_nominees").update(
            {"nominees": ArrayUnion([str(player.display_name)])}
        )

        await interaction.response.send_message(
            f"{player.mention} has been nominated for POTW!"
        )

    @app_commands.command(name="elp", description="Call for ELP")
    async def elp(self, interaction: discord.Interaction):
        await interaction.response.send_message("ELP ELLPPPPP CALL DRIADGEEEEEEEEEEEE")

    @app_commands.command(name="oath", description="Call for Oath")
    async def oath(self, interaction: discord.Interaction):
        await m_oath(interaction)

    @app_commands.command(name="dryage")
    async def dryage(self, interaction: discord.Interaction):
        await m_dryage(interaction)

    @app_commands.command(name="movie")
    async def movie(self, interaction: discord.Interaction):
        message = "Producers it's time for Movies! People are trying to do Gramiel or Speaker with their feet, come to VC!"
        await interaction.response.send_message(message)

    @app_commands.command(name="rcs")
    async def anime(self, interaction: discord.Interaction):
        await m_rcs(interaction)

    @app_commands.command(name="sker")
    async def sker_ready(self, interaction: discord.Interaction):
        await m_sker(interaction)

    @app_commands.command(name="ecr")
    async def ecr(self, interaction: discord.Interaction):
        message = """East Coast Roster:\n
    Driadge - Pot Scammer Granny Slammer\n
    SCR - Voted most likely to be kidnapped in highschool\n
    Veritus - King of the self-dox\n
    Killer - Pay2Lose Enjoyer might enact slave labor and torture friends"""
        await interaction.response.send_message(message)

    @app_commands.command(name="bigrig", nsfw=True)
    @has_any_role(ADMIN_ROLE_ID, DISCORD_MANAGER_ROLE_ID)
    async def bigrig(self, interaction: discord.Interaction):
        await m_bigrig(interaction)

    @app_commands.command(name="mapril")
    async def mapril(self, interaction: discord.Interaction):
        await m_mapril(interaction)

    @app_commands.command(name="greed")
    async def greed(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Is this mapril using this command? <a:mapGiggle:1478032348401373326>"
        )

    @app_commands.command(name="gld")
    @app_commands.default_permissions(administrator=True)
    @has_any_role(ADMIN_ROLE_ID, DISCORD_MANAGER_ROLE_ID)
    async def glad(self, interaction: discord.Interaction):
        await m_gld(interaction)

    @app_commands.command(name="glad")
    @app_commands.default_permissions(manage_roles=True)
    @has_any_role(ADMIN_ROLE_ID, DISCORD_MANAGER_ROLE_ID)
    async def eglad(self, interaction: discord.Interaction):
        await m_glad(interaction)

    @app_commands.command(name="goon-greed")
    async def goon_greed(self, interaction: discord.Interaction):
        await m_goon_greed(interaction)

    # @app_commands.command(name="og-pro")
    # async def og_pro(self, interaction: discord.Interaction):
    #    await m_og_pro(interaction)

    # @app_commands.command(name="yokai")
    # async def yokai(self, interaction: discord.Interaction):
    #    await m_yokai(interaction)

    @app_commands.command(name="announce-event-winner")
    @has_any_role(ADMIN_ROLE_ID, DISCORD_MANAGER_ROLE_ID)
    async def announce_event_winner(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        title: str,
        message: str,
        where: Literal["All", "Oath"],
    ):
        await send_winner_embed(interaction, user, title, message, where)

    @app_commands.command(name="manual-leaderboard-post")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_role(BOT_GUY_ROLE_ID)
    async def manual_leaderboard_post_command(self, interaction: discord.Interaction):
        await manual_leaderboard_post(interaction)

    @app_commands.command(
        name="ioda-list",
        description="Get the link to the IoDA spreadsheet",
    )
    async def ioda_list(self, interaction):
        return await interaction.response.send_message(
            "https://docs.google.com/document/d/1T4fut_U8Wptopw0coWCU29WCK5arAtGBy5lzlDpwswE/edit?tab=t.0"
        )

    @app_commands.command(
        name="say",
        description="Make the bot say something in current location",
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_role(BOT_GUY_ROLE_ID)
    async def say(self, interaction: discord.Interaction, message: str):

        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel

        if not isinstance(channel, Messageable):
            return

        await channel.send(content=message)

    # @app_commands.command(name="warn", description="Warn a user who oversteps")
    # @app_commands.default_permissions(manage=True)
    # @app_commands.checks.has_role(OFFICER_ROLE_ID)
    # async def warn(
    #    self, interaction: discord.Interaction, user: discord.User, message: str
    # ):
    #    await interaction.response.defer(ephemeral=True)
    #    guild = interaction.guild
    #    moderator = interaction.user
    #    dm = await user.create_dm()
    #    embed = discord.Embed(title="Warning", description=message)
    #    await dm.send(embed=embed)
    #    if not guild:
    #        return
    #    log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
    #    log_embed = discord.Embed(
    #        title=f"Warning issued for {user.display_name} ({user.mention}), issued by {moderator.display_name} ({moderator.mention})",
    #        description=message,
    #        color=discord.Color.red(),
    #    )
    #    if not isinstance(log_channel, discord.TextChannel):
    #        return
    #    await log_channel.send(embed=log_embed)
    #    return await interaction.followup.send(f"Warned {user.mention}", ephemeral=True)

    @app_commands.command(
        name="update-application",
        description="Update the application status for a user.",
    )
    @app_commands.checks.has_role(TICKET_INSPECTOR_ROLE_ID)
    async def update_application(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        certificate: Literal[
            "Champion Drakath",
            "Ultra Dage",
            "Ultra Drago",
            "Ultra Darkon",
            "Ultra Speaker",
            "Ultra Gramiel",
            "Ultra Nulgath",
        ],
        status: Literal["Awaiting Trial", "Rejected"],
        extra_message: str = "",
    ):
        await interaction.response.defer()
        app_type = certificate.split(" ")[1].lower()
        db.collection("users").document(str(user.id)).update(
            {
                f"application_statuses.{app_type}": status,
            },
        )
        try:
            extra_message = f"\n {extra_message}" if extra_message else ""
            dm = await user.create_dm()
            await dm.send(
                f"🔔 The status for your {certificate} application has been updated to {STATUS_TO_EMOJI[status]} {status}{extra_message}."
            )
        except discord.Forbidden:
            helper_channel = interaction.guild.get_channel(HELPER_CHANNEL_ID)
            if helper_channel:
                await helper_channel.send(
                    f"{user.mention}, we tried reaching out to you through DMs, but were unable to send you a message.\n🔔 The status for your {certificate} application has been updated to {STATUS_TO_EMOJI[status]} {status}{extra_message}."
                )

        await interaction.followup.send(
            f"Updated {user.mention}'s {certificate} application status to {STATUS_TO_EMOJI[status]} {status}{extra_message}",
            ephemeral=True,
        )

    @app_commands.command(
        name="promote-helper",
        description="Award a certificate for specified boss.",
    )
    @app_commands.checks.has_role(TICKET_INSPECTOR_ROLE_ID)
    async def add_role(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        certificate: Literal[
            "Champion Drakath",
            "Ultra Dage",
            "Ultra Drago",
            "Ultra Darkon",
            "Ultra Speaker",
            "Ultra Gramiel",
            "Ultra Nulgath",
        ],
        reason: Literal[
            "Passed Trial",
            "Questions + Experience",
            "Experience only",
            "Questions Only",
        ],
        extra_message: str = "",
    ):
        await interaction.response.defer(ephemeral=True)

        role = interaction.guild.get_role(BOSS_TO_CERTIFICATE[certificate])
        if not role:
            return await interaction.followup.send(
                "❌ Role not found.",
                ephemeral=True,
            )

        if role in user.roles:
            return await interaction.followup.send(
                f"⚠️ {user.mention} already has {role.mention}.",
                ephemeral=True,
            )

        if role >= interaction.guild.me.top_role:
            return await interaction.followup.send(
                "❌ I can't manage that role (it's higher than me).",
                ephemeral=True,
            )

        try:
            await user.add_roles(role)
        except discord.Forbidden:
            return await interaction.followup.send(
                "❌ Missing permissions to add role.",
                ephemeral=True,
            )

        user_ref = db.collection("users").document(str(user.id))
        user_doc = user_ref.get()
        user_data = user_doc.to_dict() or {}
        app_type = certificate.split(" ")[1].lower()
        rewarded_certs = user_data.get("certificates_rewarded", [])
        extra_message = f"\n {extra_message}" if extra_message else ""
        if certificate not in rewarded_certs:
            coins_to_add = (
                3750 if certificate in ["Ultra Speaker", "Ultra Gramiel"] else 1950
            )
            coins_to_add = 2500 if certificate == "Ultra Darkon" else coins_to_add

            update_data = {
                "coins": firestore.Increment(coins_to_add),
                "certificates_rewarded": ArrayUnion([certificate]),
            }
            db.collection("users").document(str(user.id)).update(
                {
                    f"application_statuses.{app_type}": "Approved",
                },
            )

            user_ref.set(update_data, merge=True)

            reward_text = f"\n💰 +{coins_to_add} coins awarded"
        else:
            reward_text = "\n⚠️ Reward already claimed for this certificate"

        try:
            dm = await user.create_dm()
            await dm.send(
                f"🔔 Your application has been approved, and you have been awarded {certificate} certificate.{reward_text}.{extra_message}"
            )
            await interaction.followup.send(
                f"✅ Added {role.mention} to {user.mention}. {reward_text}{extra_message}\nMessage sent via DM.",
                ephemeral=True,
            )
        except discord.Forbidden:
            helper_channel = interaction.guild.get_channel(HELPER_CHANNEL_ID)
            if helper_channel:
                await helper_channel.send(
                    f"{user.mention}, we tried reaching out to you through DMs, but were unable to send you a message.\n🫡 Your application has been approved and you have been awarded {certificate} certificate.{reward_text}{extra_message}"
                )
                await interaction.followup.send(
                    f"✅ Added {role.mention} to {user.mention}. {reward_text}{extra_message}\nAnnounced in the helper channel.",
                    ephemeral=True,
                )

        log_channel = interaction.guild.get_channel(TICKET_LOG_CHANNEL_ID)

        if log_channel:
            embed = discord.Embed(
                title=f"🟢 Certificate Awarded ({certificate})",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow(),
            )

            embed.add_field(
                name="User", value=f"{user.mention} ({user.display_name})", inline=True
            )
            embed.add_field(
                name="Awarded By",
                value=f"{interaction.user.mention} ({interaction.user.display_name})",
                inline=True,
            )
            embed.add_field(name="Reason", value=reason, inline=False)

            embed.set_footer(text=f"User ID: {user.id}")

            await log_channel.send(embed=embed)

    @app_commands.command(
        name="demote-helper",
        description="Strip a helper of a certificate.",
    )
    @app_commands.checks.has_role(TICKET_INSPECTOR_ROLE_ID)
    async def remove_role(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        certificate: Literal[
            "Champion Drakath",
            "Ultra Dage",
            "Ultra Drago",
            "Ultra Darkon",
            "Ultra Speaker",
            "Ultra Gramiel",
            "Ultra Nulgath",
        ],
        reason: str,
        announce: bool = False,
    ):
        await interaction.response.defer(ephemeral=True)

        role = interaction.guild.get_role(BOSS_TO_CERTIFICATE[certificate])
        if not role:
            return await interaction.followup.send(
                "❌ Role not found.",
                ephemeral=True,
            )

        if role not in user.roles:
            return await interaction.followup.send(
                f"⚠️ {user.mention} does not have {role.mention}.",
                ephemeral=True,
            )

        if role >= interaction.guild.me.top_role:
            return await interaction.followup.send(
                "❌ I can't manage that role.",
                ephemeral=True,
            )

        try:
            await user.remove_roles(role)
        except discord.Forbidden:
            return await interaction.followup.send(
                "❌ Missing permissions to remove role.",
                ephemeral=True,
            )

        app_type = certificate.split(" ")[1].lower()
        db.collection("users").document(str(user.id)).update(
            {
                f"application_statuses.{app_type}": "Revoked",
            },
        )
        if announce:
            try:
                dm = await user.create_dm()
                await dm.send(f"❌ Your {certificate} has been revoked.")
                await interaction.followup.send(
                    f"✅ Removed {role.mention} from {user.mention}.\nDM sent.",
                    ephemeral=True,
                )
            except discord.Forbidden:
                helper_channel = interaction.guild.get_channel(HELPER_CHANNEL_ID)
                if helper_channel:
                    await helper_channel.send(
                        f"{user.mention}, we tried reaching out to you through DMs, but were unable to send you a message.\n❌ Your {certificate} has been revoked."
                    )
                    await interaction.followup.send(
                        f"✅ Removed {role.mention} from {user.mention}.\nMentioned in the helper channel.",
                        ephemeral=True,
                    )
        else:
            await interaction.followup.send(
                f"✅ Removed {role.mention} from {user.mention}.\nNo announcement made.",
                ephemeral=True,
            )
        log_channel = interaction.guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title=f"🔴 {certificate} Removed",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow(),
            )

            embed.add_field(
                name="User", value=f"{user.mention} ({user.display_name})", inline=True
            )
            embed.add_field(
                name="Removed By",
                value=f"{interaction.user.mention} ({interaction.user.display_name})",
                inline=True,
            )
            embed.add_field(name="Reason", value=reason, inline=False)

            embed.set_footer(text=f"User ID: {user.id}")

            await log_channel.send(embed=embed)

    @app_commands.command(
        name="view-applications", description="View your application statuses"
    )
    async def view_applications(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user = interaction.user

        doc = db.collection("users").document(str(user.id)).get()
        data = doc.to_dict() or {}

        statuses = data.get("application_statuses", {})

        if not statuses:
            return await interaction.followup.send(
                "📭 You have no applications.",
                ephemeral=True,
            )

        lines = []
        for app_type, status in statuses.items():
            lines.append(f"**{app_type.title()}** — {STATUS_TO_EMOJI[status]} {status}")

        await interaction.followup.send(
            "📋 **Your Applications:**\n\n" + "\n".join(lines),
            ephemeral=True,
        )

    @app_commands.command(
        name="pending-applications",
        description="List all users with pending applications",
    )
    @app_commands.checks.has_role(TICKET_INSPECTOR_ROLE_ID)
    async def pending_applications(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if interaction.channel_id != TICKET_INSPECTORS_CHANNEL_ID:
            return await interaction.followup.send(
                "❌ This command can only be used in the Certifications channel.",
                ephemeral=True,
            )

        target_statuses = {"Awaiting Trial", "Under review"}

        results = []

        for doc in db.collection("users").stream():
            data = doc.to_dict() or {}
            statuses = data.get("application_statuses", {})

            if not isinstance(statuses, dict):
                continue  # safety guard

            for app_type, status in statuses.items():
                if status in target_statuses:
                    results.append((doc.id, app_type.lower(), status))  # normalize

        if not results:
            return await interaction.followup.send(
                "✅ No pending applications found.",
                ephemeral=True,
            )

        results.sort(key=lambda x: (x[1], x[2]))

        lines = []
        for uid, app_type, status in results[:25]:
            member = interaction.guild.get_member(int(uid))
            name = member.display_name if member else f"<@{uid}>"

            lines.append(
                f"• {name} — **{app_type.title()}** ({STATUS_TO_EMOJI[status]} {status})"
            )

        extra = len(results) - 25
        if extra > 0:
            lines.append(f"\n… and {extra} more")

        await interaction.followup.send(
            "📋 **Pending Applications:**\n\n" + "\n".join(lines), ephemeral=True
        )

    @app_commands.command(name="leaderboard", description="View leaderboards")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel_id = interaction.channel_id
        if channel_id not in ALLOWED_COMMANDS_CHANNELS:
            allowed_mentions = ", ".join(
                [f"<#{channel}>" for channel in ALLOWED_COMMANDS_CHANNELS]
            )
            await interaction.followup.send(
                f"❌ This command can only be used in {allowed_mentions}.",
                ephemeral=True,
            )
            return
        guild = interaction.guild
        if not guild:
            return
        embed = await record_holder("points", guild)
        await interaction.followup.send(embed=embed, view=LeaderboardView())

    @app_commands.command(name="timeout", description="Timeout an officer for 1 hour.")
    async def timeout(self, interaction: discord.Interaction, target: discord.Member):
        await interaction.response.defer()
        doc = db.collection("users").document(str(interaction.user.id)).get()
        data = doc.to_dict() or {}
        last_timeout = data.get("last_timeout")
        if last_timeout and (datetime.now(timezone.utc) - last_timeout) < timedelta(
            days=30
        ):
            await interaction.followup.send(
                "You can only timeout a member once per 30 days.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        if not guild:
            return
        transcended_role = guild.get_role(TRANSCENDED_ROLE_ID)
        user_roles = interaction.user.roles
        if transcended_role not in user_roles:
            await interaction.followup.send(
                "You are not a transcended member.",
                ephemeral=True,
            )
            return

        target_roles = target.roles
        oathsworn_role = guild.get_role(OATHSWORN_ROLE_ID)

        if oathsworn_role not in target_roles:
            await interaction.followup.send(
                "Target is not an oathsworn member.",
                ephemeral=True,
            )
            return

        if target.guild_permissions.administrator:
            await interaction.followup.send(
                "You cannot timeout an administrator.",
                ephemeral=True,
            )
            return

        hour_from_now = datetime.now(timezone.utc) + timedelta(hours=1)
        await target.edit(
            timed_out_until=hour_from_now, reason=f"Timed out by {interaction.user}"
        )
        now = datetime.now(timezone.utc)

        db.collection("users").document(str(interaction.user.id)).set(
            {"last_timeout": now}, merge=True
        )
        await interaction.followup.send(
            f"{target.mention} has been timed out for 1 hour.",
            ephemeral=True,
        )
        return

    @app_commands.command(
        name="ioda", description="See how much AC you need to spend for an IoDA"
    )
    async def ioda(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        per_spin: Literal["1", "2", "6"],
    ):
        await interaction.response.defer()
        channel_id = interaction.channel_id
        if channel_id not in ALLOWED_COMMANDS_CHANNELS:
            await interaction.followup.send(
                "This command is not allowed in this channel.", ephemeral=True
            )
            return
        user_doc = db.collection("users").document(str(user.id)).get()
        if not user_doc.exists:
            await interaction.followup.send("User not found.", ephemeral=True)
            return
        user_data = user_doc.to_dict()
        ccid = user_data.get("ccid")
        if not ccid:
            await interaction.followup.send("User has no CCID.", ephemeral=True)
            return

        inventory = await fetch_inventory(ccid)
        treasure_potions = 0
        for item in inventory:
            if item.get("strName") == "Treasure Potion":
                treasure_potions = int(item.get("intCount", 0))

        missing_potions = 1000 - int(treasure_potions)
        days_non_mem = math.ceil(missing_potions / int(per_spin)) * 7
        days_mem = math.ceil(missing_potions / int(per_spin))
        days_mem -= days_mem // 7
        acs = math.ceil(missing_potions / int(per_spin)) * 200
        embed = discord.Embed(
            title="How far off Item of Digital Awesomeness?",
            description="",
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="Currently", value=f"{treasure_potions}/1000 potions", inline=False
        )

        embed.add_field(
            name="Using weekly spins",
            value=f"{format_duration(days_non_mem)}",
            inline=False,
        )

        embed.add_field(
            name="Using daily spins <:legendaqw:1498781178075943043>",
            value=f"{format_duration(days_mem)}",
            inline=False,
        )

        embed.add_field(
            name="Using ACs", value=f"{acs}<:acaqw:1498781113127145482>", inline=False
        )
        return await interaction.followup.send(embed=embed)

    @app_commands.command(name="test", description="test layout")
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_role(BOT_GUY_ROLE_ID)
    async def testl(self, interaction: discord.Interaction):
        layout = TestLayout()

        await interaction.response.send_message(
            view=layout,
        )

    @app_commands.command(name="css", description="CSS tutorial")
    async def css(self, interaction: discord.Interaction):
        basic_url = "https://youtu.be/ky-MIAIdrfU?si=665iAMcKfJIzkNYr"
        ultra_url = "https://youtu.be/LekEuqIP3dw?si=_IbmPrNTd96_q8ZU"
        embed = discord.Embed(
            title="Alvii's guide to Chrono ShadowSlayer",
            description=f"Check out this video for the basics: {basic_url}\n\nCheck out this video for Ultras: {ultra_url}",
            color=discord.Color.green(),
        )
        embed.set_image(
            url="https://www.artix.com/media/5921/promo-2024calendar-pre-order.jpg?width=1170px&height=658px&mode=crop"
        )
        return await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="register-lol-team", description="Register your team for LoL Tourney"
    )
    @app_commands.checks.has_any_role(INITIATE_ROLE_ID, UNSWORN_ROLE_ID)
    async def register_team(self, interaction: discord.Interaction, team_name: str):
        user = interaction.user

        team_ref = db.collection("league_teams").document(team_name)
        team_doc = team_ref.get()

        # Team already exists
        if team_doc.exists:
            await interaction.response.send_message(
                f"{team_name} is already registered for LoL Tourney!", ephemeral=True
            )
            return

        # Create team
        team_ref.set(
            {
                "team_name": team_name,
                "captain": user.id,
                "player1": user.id,
                "player2": None,
                "player3": None,
                "player4": None,
                "player5": None,
                "substitute": None,
            }
        )

        return await interaction.response.send_message(
            f"{team_name} has been registered for LoL Tourney!"
        )

    @app_commands.command(
        name="lfg-lol", description="Mark yourself as available for LoL Tourney"
    )
    @app_commands.checks.has_any_role(INITIATE_ROLE_ID, UNSWORN_ROLE_ID)
    async def lfg_lol(self, interaction: discord.Interaction):

        user = interaction.user

        # Prevent LFG if already on team
        existing_team = get_user_team(user.id)

        if existing_team:
            await interaction.response.send_message(
                f"You are already on {existing_team['team_name']}!", ephemeral=True
            )
            return

        lfg_ref = db.collection("lfg_lol").document(str(user.id))
        lfg_doc = lfg_ref.get()

        # Already in LFG
        if lfg_doc.exists:
            await interaction.response.send_message(
                "You are already in the LoL LFG list!", ephemeral=True
            )
            return

        lfg_ref.set(
            {
                "user_id": user.id,
                "display_name": user.display_name,
                "status": "available",
            }
        )

        await interaction.response.send_message(
            "You have been added to the LoL LFG list!"
        )

    @app_commands.command(
        name="view-lfg", description="View all users looking for team"
    )
    @app_commands.checks.has_any_role(INITIATE_ROLE_ID, UNSWORN_ROLE_ID)
    async def view_lfg(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        if channel_id != LFG_LOL_ID:
            await interaction.response.send_message(
                "This command can only be used in the LoL LFG channel!", ephemeral=True
            )
            return
        users = [
            doc.to_dict()
            for doc in db.collection("lfg_lol").where("status", "==", "available").get()
        ]
        layout = LFGPlayersLayout(users)
        return await interaction.response.send_message(view=layout, ephemeral=True)

    @app_commands.command(name="join-lol-team", description="Join an existing LoL team")
    @app_commands.checks.has_any_role(INITIATE_ROLE_ID, UNSWORN_ROLE_ID)
    async def join_lol_team(self, interaction: discord.Interaction):

        teams = db.collection("league_teams").stream()

        await interaction.response.send_message(
            "Select a team to join:", view=TeamView(teams), ephemeral=True
        )

    @app_commands.command(
        name="view-lol-teams", description="View all registered LoL teams"
    )
    @app_commands.checks.has_any_role(INITIATE_ROLE_ID, UNSWORN_ROLE_ID)
    async def view_lol_teams(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        if channel_id != LFG_LOL_ID:
            await interaction.response.send_message(
                "This command can only be used in the LoL LFG channel!", ephemeral=True
            )
            return

        teams = db.collection("league_teams").get()
        layout = LeagueTeamsLayout(teams)
        return await interaction.response.send_message(view=layout, ephemeral=True)

    @app_commands.command(name="png", description="Render AQW PNG")
    @app_commands.describe(username="AQW username")
    @app_commands.checks.has_any_role(BOT_GUY_ROLE_ID)
    async def png_command(self, interaction: discord.Interaction, username: str):

        await interaction.response.defer()

        try:
            image = await render_png(username)

            await interaction.followup.send(
                file=discord.File(image, filename=f"{username}.png")
            )

        except Exception as e:
            await interaction.followup.send(f"Error: {e}")

    @app_commands.command(
        name="room-codes", description="Get room codes for your claimed ticket"
    )
    async def room_codes_command(self, interaction: discord.Interaction):
        user = interaction.user
        user_data = db.collection("users").document(str(user.id)).get()
        active_ticket = user_data.get("active_ticket")

        if not active_ticket:
            return await interaction.response.send_message(
                "❌ You must claim a ticket first!", ephemeral=True
            )

        ticket_data = db.collection("tickets").document(active_ticket).get()

        bosses = ticket_data.get("bosses")
        room_code = ticket_data.get("room")
        lines = []

        for boss in bosses:
            custom_tickets = {"spamming", "testing", "until drop"}
            if ticket_data.get("type") in custom_tickets:
                if "TempleShrine" in boss:
                    rooms = "templeshrine"
                elif "Flame Usurper" in boss:
                    rooms = "flameusurper"
                else:
                    rooms = boss
            else:
                rooms = get_boss_room(boss)

            if not rooms:
                continue

            # Split multiple rooms by comma
            room_list = [r.strip() for r in rooms.split(",")]

            for room in room_list:
                lines.append(f"```/join {room}-{room_code}```")

        rooms_text = "".join(lines)

        await interaction.response.send_message(
            f"📋 **Room codes:**\n{rooms_text}", ephemeral=True
        )

    @app_commands.command(name="test-claim", description="Test claim gif")
    async def test_claim(
        self,
        interaction: discord.Interaction,
        gif: str = "akame-claim.gif",
        is_claiming: bool = True,
    ):

        if interaction.user.display_name in {"Proxy", "Mapril"}:
            image = await gif_claim(
                interaction.user.display_name,
                is_claiming,
                "(1/7)",
                interaction.user,
                gif,
            )
            await interaction.channel.send(file=discord.File(image, "claim.gif"))
        else:
            await interaction.response.send_message(
                "You are not eligible to test.", ephemeral=True
            )

    @app_commands.command(name="staff", description="Send staff panel")
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_role(BOT_GUY_ROLE_ID)
    async def staff(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        lead_view = LeadLayout()
        officer_view = OfficerLayout()
        ex_view = ExLayout()
        end_view = EndLayout()
        channel = interaction.channel

        await channel.send(view=lead_view)
        await channel.send(view=officer_view)
        await channel.send(view=ex_view)
        await channel.send(view=end_view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Extra(bot))
