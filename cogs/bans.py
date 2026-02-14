import discord
from discord import app_commands
from discord.ext import commands

from config import OATHSWORN_ROLE_ID, TICKET_LOG_CHANNEL_ID
from extra_commands.ban_embed import build_ban_list_embed
from extra_commands.bans import add_ban, get_all_bans, is_user_banned, remove_ban
from extra_commands.log_ban_embed import build_ban_log_embed
from extra_commands.utils import is_ban_channel


class Bans(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="banlist", description="View all banned users")
    @app_commands.checks.has_role(OATHSWORN_ROLE_ID)
    @is_ban_channel()
    async def banlist(self, interaction: discord.Interaction):

        bans = get_all_bans()
        embed = build_ban_list_embed(bans)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Add a user to the ban list")
    @app_commands.describe(username="User to ban", reason="Reason for the ban")
    @app_commands.checks.has_role(OATHSWORN_ROLE_ID)
    @is_ban_channel()
    async def ban(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None,
        username: str,
        reason: str,
    ):
        # Prevent self-ban

        # Check if already banned
        if is_user_banned(username):
            return await interaction.response.send_message(
                "⚠️ That user is already banned.",
                ephemeral=True,
            )
        discord_id = user.id if user else None
        # Add ban
        add_ban(
            discord_id=discord_id,
            username=username,
            reason=reason,
            banned_by=interaction.user.id,
        )

        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message(
                "❌ This command must be used in a server.",
                ephemeral=True,
            )

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)

        if isinstance(log_channel, discord.TextChannel):
            embed = build_ban_log_embed(
                guild=guild,
                target_id=username,
                moderator_id=interaction.user.id,
                reason=reason,
                action="ban",
            )
            await log_channel.send(embed=embed)

        await interaction.response.send_message(
            f"🚫 **{username}** has been banned.\nReason: {reason}",
            ephemeral=True,
        )

    @app_commands.command(name="unban", description="Remove a user from ban list")
    @app_commands.describe(username="User to unban")
    @app_commands.checks.has_role(OATHSWORN_ROLE_ID)
    @is_ban_channel()
    async def unban(
        self,
        interaction: discord.Interaction,
        username: str,
    ):
        success = remove_ban(username)

        if not success:
            return await interaction.response.send_message(
                "❌ That user is not banned.",
                ephemeral=True,
            )
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message(
                "❌ This command must be used in a server.",
                ephemeral=True,
            )

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)

        if isinstance(log_channel, discord.TextChannel):
            embed = build_ban_log_embed(
                guild=guild,
                target_id=username,
                moderator_id=interaction.user.id,
                reason=None,
                action="ban",
            )
            await log_channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ **{username}** has been unbanned.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Bans(bot))
