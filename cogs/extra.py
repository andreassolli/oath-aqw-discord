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
    NULGATH_CERTIFICATE_ID,
    OATHSWORN_ROLE_ID,
    SPEAKER_CERTIFICATE_ID,
    TICKET_INSPECTOR_ROLE_ID,
    TICKET_INSPECTORS_CHANNEL_ID,
    TICKET_LOG_CHANNEL_ID,
)
from economy.gamba.coinflip import run_coinflip
from economy.gamba.doom_view import DoomSpinView
from economy.gamba.utils import has_spun_today
from economy.gamba.yanken_accept_view import RPSAcceptView
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
from extra_commands.utils import (
    check_missing_badges,
    count_messages,
    elect_potw,
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
from ticket_help.utils.experienced import StartView
from user_verification.utils import change_roles

BOSS_TO_CERTIFICATE = {
    # "Champion Drakath": DRAKATH_CERTIFICATE_ID,
    # "Ultra Dage": DAGE_CERTIFICATE_ID,
    # "Ultra Drago": DRAGO_CERTIFICATE_ID,
    # "Ultra Darkon": DARKON_CERTIFICATE_ID,
    "Ultra Speaker": SPEAKER_CERTIFICATE_ID,
    "Ultra Gramiel": GRAMIEL_CERTIFICATE_ID,
    # "Ultra Nulgath": NULGATH_CERTIFICATE_ID,
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
    @app_commands.checks.has_role(OATHSWORN_ROLE_ID)
    async def nominate(self, interaction: discord.Interaction, player: discord.Member):
        is_oath_member = any(role.id == INITIATE_ROLE_ID for role in player.roles)
        if not is_oath_member:
            await interaction.response.send_message(
                f"{player.mention} is not in Oath Guild and cannot be nominated for POTW."
            )
            return

        db.collection("meta").document("potw_nominees").update(
            {"nominees": ArrayUnion([str(player.id)])}
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
        status: Literal["Awaiting Trial", "Rejected", "Approved"],
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
            f"Updated {user.mention}'s application status to {STATUS_TO_EMOJI[status]} {status}",
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
        reason: Literal["Passed Trial", "Questions + Experience", "Experience only"],
        announce: bool = False,
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

        if certificate not in rewarded_certs:
            coins_to_add = (
                3750 if certificate in ["Ultra Speaker", "Ultra Gramiel"] else 1950
            )
            coins_to_add = 2500 if certificate == "Ultra Darkon" else coins_to_add

            update_data = {
                "coins": firestore.Increment(coins_to_add),
                "certificates_rewarded": ArrayUnion([certificate]),
                f"application_statuses.{app_type}": "Approved",
            }

            user_ref.set(update_data, merge=True)

            reward_text = f"\n💰 +{coins_to_add} coins awarded"
        else:
            reward_text = "\n⚠️ Reward already claimed for this certificate"

        if not announce:
            await interaction.followup.send(
                f"✅ Added {role.mention} to {user.mention}. {reward_text}\nRemember to announce it {user.mention} yourself, and include the coins they were given!",
                ephemeral=True,
            )
        else:
            try:
                dm = await user.create_dm()
                await dm.send(
                    f"🔔 Your application has been approved, and you have been awarded {certificate} certificate.{reward_text}."
                )
                await interaction.followup.send(
                    f"✅ Added {role.mention} to {user.mention}. {reward_text}\nMessage sent via DM.",
                    ephemeral=True,
                )
            except discord.Forbidden:
                helper_channel = interaction.guild.get_channel(HELPER_CHANNEL_ID)
                if helper_channel:
                    await helper_channel.send(
                        f"{user.mention}, we tried reaching out to you through DMs, but were unable to send you a message.\n🫡 Your application has been approved and you have been awarded {certificate} certificate.{reward_text}"
                    )
                    await interaction.followup.send(
                        f"✅ Added {role.mention} to {user.mention}. {reward_text}\nAnnounced in the helper channel.",
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
        await interaction.response.defer()
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
            "📋 **Pending Applications:**\n\n" + "\n".join(lines),
        )

    @app_commands.command(name="sync-roles", description="Apply roles from DB")
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_role(BOT_GUY_ROLE_ID)
    async def sync_roles(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            return await interaction.followup.send(
                "❌ Guild not found.", ephemeral=True
            )

        users = list(db.collection("users").stream())

        updated = 0
        skipped = 0
        failed = 0
        coins_to_add = 7500
        for user_doc in users:
            try:
                data = user_doc.to_dict() or {}

                member = guild.get_member(int(user_doc.id))
                if not member:
                    skipped += 1
                    continue

                user_ref = db.collection("users").document(user_doc.id)

                user_ref.update(
                    {
                        "coins": firestore.Increment(coins_to_add),
                        "certificates_rewarded": ["Ultra Gramiel", "Ultra Speaker"],
                    }
                )

                verified = data.get("verified", False)
                guild_name = data.get("guild")

                if not verified:
                    await change_roles(
                        member,
                        is_join_event=False,
                        verified_guild=None,
                        verified_at_all=False,
                    )
                    updated += 1
                    continue

                await change_roles(
                    member,
                    is_join_event=False,
                    verified_guild=guild_name,
                )

                updated += 1

            except Exception as e:
                failed += 1

        await interaction.followup.send(
            f"✅ Role sync complete\nUpdated: {updated}\nSkipped: {skipped}\nFailed: {failed}",
            ephemeral=True,
        )

    @app_commands.command(
        name="compare-role-db",
        description="Compare role members with database users",
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_role(BOT_GUY_ROLE_ID)
    async def compare_role_db(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
    ):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            return await interaction.followup.send(
                "❌ Guild not found.", ephemeral=True
            )

        role_members = role.members
        role_ids = {member.id for member in role_members}

        db_users = list(
            db.collection("users").where("qualified_helper", "==", True).stream()
        )
        db_ids = {int(doc.id) for doc in db_users if doc.id.isdigit()}

        in_role_not_db = role_ids - db_ids
        in_db_not_role = db_ids - role_ids

        in_db_not_role = {uid for uid in in_db_not_role if guild.get_member(uid)}

        def format_users(user_ids):
            return "\n".join(f"<@{uid}>" for uid in list(user_ids)[:20]) or "None"

        embed = discord.Embed(
            title="🔍 Role ↔ DB Comparison",
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name=f"👥 In role but NOT in DB ({len(in_role_not_db)})",
            value=format_users(in_role_not_db),
            inline=False,
        )

        embed.add_field(
            name=f"📄 In DB but missing role ({len(in_db_not_role)})",
            value=format_users(in_db_not_role),
            inline=False,
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="scan-messages")
    @app_commands.default_permissions(administrator=True)
    async def scan_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        counts = await count_messages(channel)

        update_message_counts(counts)

        await interaction.followup.send(
            f"✅ Processed {len(counts)} users.",
            ephemeral=True,
        )

    @app_commands.command(
        name="mark-beta-users",
        description="Mark all users with a role as beta participants",
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_role(BOT_GUY_ROLE_ID)
    async def mark_beta_users(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
    ):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            return await interaction.followup.send(
                "❌ Guild not found.", ephemeral=True
            )

        role_members = role.members

        updated = 0

        batch = db.batch()
        count = 0

        for member in role_members:
            ref = db.collection("users").document(str(member.id))

            batch.set(
                ref,
                {"participated_in_beta": False},
                merge=True,
            )
            updated += 1
            count += 1

            if count % 500 == 0:
                batch.commit()
                batch = db.batch()

        # Commit remaining
        batch.commit()

        await interaction.followup.send(
            f"✅ Marked **{updated} users** as beta participants.",
            ephemeral=True,
        )

    @app_commands.command(
        name="role-add-bulk",
        description="Give all members of one role another role",
    )
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_role(BOT_GUY_ROLE_ID)
    async def role_add_bulk(
        self,
        interaction: discord.Interaction,
        from_role: discord.Role,
        to_role: discord.Role,
    ):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            return await interaction.followup.send(
                "❌ Guild not found.", ephemeral=True
            )

        if to_role >= guild.me.top_role:
            return await interaction.followup.send(
                "❌ I cannot assign that role (it's higher than me).",
                ephemeral=True,
            )

        members = from_role.members

        updated = 0
        skipped = 0
        failed = 0

        for member in members:
            user_ref = db.collection("users").document(str(member.id))

            user_ref.update(
                {
                    "coins": firestore.Increment(7500),
                    "certificates_rewarded": ["Ultra Gramiel", "Ultra Speaker"],
                }
            )
            try:
                if to_role in member.roles:
                    skipped += 1
                    continue

                await member.add_roles(to_role, reason="Bulk role assignment")
                updated += 1

            except discord.Forbidden:
                failed += 1
            except Exception:
                failed += 1

        await interaction.followup.send(
            f"✅ Done.\n"
            f"Updated: {updated}\n"
            f"Skipped (already had role): {skipped}\n"
            f"Failed: {failed}",
            ephemeral=True,
        )

    @app_commands.command(name="leaderboard", description="View leaderboards")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel = interaction.channel
        if channel not in ALLOWED_COMMANDS_CHANNELS:
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Extra(bot))
