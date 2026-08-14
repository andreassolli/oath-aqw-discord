import math
from datetime import datetime, timedelta, timezone
from typing import Literal
import json
import discord
from discord import app_commands
from discord.abc import Messageable
from discord.ext import commands
from google.cloud import firestore
from google.cloud import firestore as gc_firestore
from google.cloud.firestore import ArrayUnion, Increment

from config import (
    ADMIN_ROLE_ID,
    ALLOWED_COMMANDS_CHANNELS,
    BOT_GUY_ROLE_ID,
    DAGE_CERTIFICATE_ID,
    DARKON_CERTIFICATE_ID,
    DISCORD_MANAGER_ROLE_ID,
    DRAGO_CERTIFICATE_ID,
    DRAKATH_CERTIFICATE_ID,
    GRAMIEL_CERTIFICATE_ID,
    HELPER_CHANNEL_ID,
    INITIATE_ROLE_ID,
    NULGATH_CERTIFICATE_ID,
    OATHSWORN_ROLE_ID,
    SPEAKER_CERTIFICATE_ID,
    SUGGESTIONS_CATEGORY,
    TICKET_INSPECTOR_ROLE_ID,
    TICKET_INSPECTORS_CHANNEL_ID,
    TICKET_LOG_CHANNEL_ID,
    TRANSCENDED_ROLE_ID,
)
from extra_commands.ioda_view import IodaView
from extra_commands.page_pending_cert import PendingApplicationsView
from extra_commands.record_holder import record_holder
from extra_commands.record_view import LeaderboardView
from extra_commands.utils import (
    check_missing_badges,
    elect_potw,
    format_duration,
    has_any_role,
    manual_leaderboard_post,
    send_winner_embed,
)
from firebase_client import db
from panels.spam_cache import SPAM_PANEL_CACHE
from panels.spam_view import SpamCreateView
from panels.staff_panel import (
    EndLayout,
    ExLayout,
    LeadLayout,
    OfficerLayout,
)
from ticket_help.tickets.points import get_boss_room, get_spam_boss_room
from ticket_help.tickets.utils import monster_autocomplete
from user_profile.utils import fetch_inventory
with open("ioda_list.json", "r", encoding="utf-8") as ioda:
    IODA_ITEMS = json.load(ioda)

with open("kbioda_list.json", "r", encoding="utf-8") as kbioda:
    KBIODA_ITEMS = json.load(kbioda)

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

    @app_commands.command(name="elect-potw", description="Elect a player for POTW")
    @app_commands.checks.has_role(DISCORD_MANAGER_ROLE_ID)
    async def elect_potw(
        self, interaction: discord.Interaction, player: discord.Member
    ):
        await elect_potw(player)

        # Clear all nominees
        batch = db.batch()
        for doc in db.collection("potw_nominees").stream():
            batch.delete(doc.reference)

        # Clear all nominators
        for doc in db.collection("potw_nominators").stream():
            batch.delete(doc.reference)

        batch.commit()

        await interaction.response.send_message(
            f"🎉 {player.mention} has been elected POTW!\n"
            "🗑️ All POTW nominations have been reset."
        )

    @app_commands.command(name="nominate", description="Nominate a player for POTW")
    @app_commands.checks.has_any_role(INITIATE_ROLE_ID)
    async def nominate(self, interaction: discord.Interaction, player: discord.Member):
        is_oath_member = any(role.id == INITIATE_ROLE_ID for role in player.roles)
        if not is_oath_member:
            await interaction.response.send_message(
                f"{player.mention} is not in Oath Guild and cannot be nominated for POTW.",
                ephemeral=True,
            )
            return

        if player.id == interaction.user.id:
            await interaction.response.send_message(
                f"You cannot nominate yourself.", ephemeral=True
            )
            return

        nominator_ref = db.collection("potw_nominators").document(
            str(interaction.user.id)
        )

        if nominator_ref.get().exists:
            await interaction.response.send_message(
                "You have already used your POTW nomination.",
                ephemeral=True,
            )
            return

        doc_ref = db.collection("potw_nominees").document(
            str(player.display_name.lower())
        )
        doc = doc_ref.get()

        if doc.exists:
            doc_ref.update(
                {
                    "count": Increment(1),
                    "nominated_by": ArrayUnion([interaction.user.display_name.lower()]),
                }
            )

        else:
            doc_ref.set(
                {
                    "name": player.display_name.lower(),
                    "count": 1,
                    "nominated_by": [interaction.user.display_name.lower()],
                }
            )

        nominator_ref.set({"nominated_player": player.display_name})
        await interaction.response.send_message(
            f"{player.mention} has been nominated for POTW!", ephemeral=True
        )

    @app_commands.command(name="elp", description="Call for ELP")
    async def elp(self, interaction: discord.Interaction):
        await interaction.response.send_message("ELP ELLPPPPP CALL DRIADGEEEEEEEEEEEE")

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
        description="Show stats for most IoDA'ed items",
    )
    async def ioda_list(self, interaction: discord.Interaction):

        items = IODA_ITEMS['data']

        # Sort descending by count (ALREADY SORTED)
        # items.sort(key=lambda x: x["count"], reverse=True)

        view = IodaView(items)

        await interaction.response.send_message(
            embed=view.make_embed(),
            view=view
        )

    @app_commands.command(
        name="kbioda-list",
        description="Show stats for most IoDA'ed items",
    )
    async def kbioda_list(self, interaction: discord.Interaction):

        items = KBIODA_ITEMS['data']

        # Sort descending by count (ALREADY SORTED)
        # items.sort(key=lambda x: x["count"], reverse=True)

        view = IodaView(items)

        await interaction.response.send_message(
            embed=view.make_embed(),
            view=view
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
    async def pending_applications(
        self,
        interaction: discord.Interaction,
        filter: Literal["Under review", "Awaiting Trial", "All"] = "All",
    ):
        await interaction.response.defer(ephemeral=True)

        if interaction.channel_id != TICKET_INSPECTORS_CHANNEL_ID:
            return await interaction.followup.send(
                "❌ This command can only be used in the Certifications channel.",
                ephemeral=True,
            )

        target_statuses = (
            {"Awaiting Trial", "Under review"}
            if filter == "All"
            else {filter}
        )

        results = []

        for doc in db.collection("users").stream():
            data = doc.to_dict() or {}
            statuses = data.get("application_statuses", {})

            if not isinstance(statuses, dict):
                continue

            for app_type, status in statuses.items():
                if status in target_statuses:
                    results.append((doc.id, app_type, status))

        if not results:
            return await interaction.followup.send(
                "✅ No pending applications found.",
                ephemeral=True,
            )

        results.sort(key=lambda x: (x[1].lower(), x[2]))

        # Build all result lines
        lines = []

        for uid, app_type, status in results:
            try:
                member = interaction.guild.get_member(int(uid))
            except ValueError:
                member = None

            name = member.display_name if member else f"<@{uid}>"

            lines.append(
                f"• {name} — **{app_type}** "
                f"({STATUS_TO_EMOJI[status]} {status})"
            )

        # 25 results per page
        page_size = 25
        pages = []

        total_pages = (len(lines) + page_size - 1) // page_size

        for i in range(0, len(lines), page_size):
            page_lines = lines[i:i + page_size]
            page_number = (i // page_size) + 1

            pages.append(
                f"📋 **Pending Applications** — Page {page_number}/{total_pages}\n\n"
                + "\n".join(page_lines)
            )

        view = PendingApplicationsView(pages)

        await interaction.followup.send(
            content=pages[0],
            view=view,
            ephemeral=True,
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

    @app_commands.command(name="mute", description="Mute a discord member for 1 or 5 minutes.")
    async def mute(self, interaction: discord.Interaction, target: discord.Member, duration: Literal["1","5"]):
        await interaction.response.defer()

        guild = interaction.guild
        if not guild:
            return

        officer_role = guild.get_role(OATHSWORN_ROLE_ID)
        user_roles = interaction.user.roles
        if officer_role not in user_roles:
            return await interaction.followup.send(
                "Only officers may mute others.",
                ephemeral=True,
            )
        if target.guild_permissions.administrator:
            return await interaction.followup.send(
                "You cannot timeout an administrator.",
                ephemeral=True,
            )

        duration_from_now = datetime.now(timezone.utc) + timedelta(minutes=int(duration))
        await target.edit(
            timed_out_until=duration_from_now, reason=f"Timed out by {interaction.user}"
        )
        return await interaction.followup.send(
            f"{target.mention} has been timed out for {duration} minutes.",
            ephemeral=True,
        )


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
        name="add-bosses",
        description="Add bosses to your spam ticket"
    )
    @app_commands.autocomplete(
        monster1=monster_autocomplete,
        monster2=monster_autocomplete,
        monster3=monster_autocomplete,
        monster4=monster_autocomplete,
        monster5=monster_autocomplete,
    )
    async def update_spam_panel(
        self,
        interaction: discord.Interaction,
        monster1: str | None = None,
        monster2: str | None = None,
        monster3: str | None = None,
        monster4: str | None = None,
        monster5: str | None = None,
    ):
        cache = SPAM_PANEL_CACHE.get(interaction.user.id)

        if not cache:
            return await interaction.response.send_message(
                "The spam panel hasn't been created yet.",
                ephemeral=True,
            )

        new_bosses = [
            boss for boss in (
                monster1,
                monster2,
                monster3,
                monster4,
                monster5,
            )
            if boss
        ]

        if not new_bosses:
            return await interaction.response.send_message(
                "You need to provide at least one boss.",
                ephemeral=True,
            )

        bosses = cache.get("bosses", [])

        bosses.extend(new_bosses)

        bosses = list(dict.fromkeys(bosses))

        view = SpamCreateView(
            servers=cache["servers"],
            type=cache["type"],
            practice=cache["is_practice"],
            bosses=bosses,
        )

        await interaction.response.send_message(
            f"Current bosses: {', '.join(bosses)}",
            view=view,
            ephemeral=True,
        )

        # Store the updated state
        cache["bosses"] = bosses
        cache["view"] = view

        return

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
        type = ticket_data.get("type")
        lines = []

        for boss in bosses:
            if type == "spamming":
                spam_boss = get_spam_boss_room(boss)
                rooms = spam_boss.get("room")
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
        embed = discord.Embed(
            color=discord.Colour(7344907),
        )

        embed.set_image(
            url="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/oathstaff.png"
        )
        # await channel.send(embed=embed)
        # await channel.send(view=lead_view)
        await channel.send(view=officer_view)
        ex_embed = discord.Embed(
            color=discord.Colour(7344907),
        )

        ex_embed.set_image(
            url="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/exofficers.png"
        )
        await channel.send(embed=ex_embed)
        await channel.send(view=ex_view)
        await channel.send(view=end_view)
        await interaction.followup.send("Sent panels")

    @app_commands.command(
        name="helper-stats",
        description="View your stats for helping in tickets."
    )
    async def helper_stats(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()

        user_ref = db.collection("users").document(str(interaction.user.id))
        user_doc = user_ref.get()

        if not user_doc.exists:
            await interaction.followup.send(
                "You don't have any helper statistics yet."
            )
            return

        user_data = user_doc.to_dict() or {}

        tickets_claimed = user_data.get("tickets_claimed", 0)
        total_points = user_data.get("total_points", 0)
        boss_clears = user_data.get("boss_clears", {})

        # Sort bosses by clears (highest first)
        sorted_bosses = sorted(
            boss_clears.items(),
            key=lambda x: (-x[1], x[0])
        )

        if sorted_bosses:
            boss_text = "\n".join(
                f"• {boss} — `{count}`"
                for boss, count in sorted_bosses
            )
        else:
            boss_text = "No bosses completed."
#\n <:complete_ticket:1505157129252634706> **Tickets Claimed:** `{tickets_claimed}`
        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Helper Stats <:claiming:1505158455412002846>",
            description=f"\n<:medal:1505158451179819119> **Total Points:** `{total_points}`\n\n<:star:1503523567898460311> **Bosses Completed**\n{boss_text}",
            color=discord.Colour(7344907),
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="suggest-feature",
        description="Create a private channel to discuss a feature."
    )
    async def suggest_feature(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if guild is None:
            return

        category = guild.get_channel(SUGGESTIONS_CATEGORY)
        oathsworn_role = guild.get_role(OATHSWORN_ROLE_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False,
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
            ),
        }

        # Give all Oathsworn members access
        if oathsworn_role:
            overwrites[oathsworn_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            )

        channel = await guild.create_text_channel(
            name=f"feature-{interaction.user.name}".lower(),
            category=category,
            overwrites=overwrites,
            reason=f"Feature suggestion by {interaction.user}",
        )

        await interaction.followup.send(
            f"✅ Created {channel.mention}.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Extra(bot))
