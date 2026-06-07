import discord
from discord.ext import commands

from extra_commands.transcended_colors import setup_color_panel
from firebase_client import db
from ticket_help import setup_ticket_system
from ticket_help.commands.admin import (
    add_boss,
    adjust_points,
    clear_active_ticket_command,
    delete_boss,
    delete_type,
    lookup_points,
    reload_point_rules,
    remove_claimer,
    reset_all_points,
    set_boss_points,
    set_user_points,
)
from ticket_help.utils.experienced_panel import setup_application_panel
from ticket_help.utils.message_logging import log_ticket_message_event


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._started: bool = False

    async def cog_load(self):
        """Register slash commands when the cog is loaded."""
        tree = self.bot.tree

        tree.add_command(reload_point_rules)
        tree.add_command(set_boss_points)
        tree.add_command(reset_all_points)
        tree.add_command(set_user_points)
        tree.add_command(add_boss)
        tree.add_command(delete_boss)
        tree.add_command(lookup_points)
        tree.add_command(delete_type)
        tree.add_command(adjust_points)
        tree.add_command(remove_claimer)
        tree.add_command(clear_active_ticket_command)

    @commands.Cog.listener()
    async def on_ready(self):
        # Prevent double-start on reload / reconnect
        if self._started:
            return

        self._started = True
        await self.bot.wait_until_ready()
        await setup_color_panel(self.bot)
        await setup_application_panel(self.bot)
        # await setup_ticket_system(self.bot)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if isinstance(message.channel, discord.Thread):
            return

        if not isinstance(message.channel, discord.TextChannel):
            return

        docs = (
            db.collection("tickets")
            .where("channel_id", "==", message.channel.id)
            .limit(1)
            .get()
        )

        if not docs:
            return

        ticket_name = docs[0].id

        files = [await a.to_file() for a in message.attachments]

        await log_ticket_message_event(
            self.bot,
            ticket_name,
            f"💬 {message.author.display_name}: {message.content}",
            files,
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if isinstance(after.channel, discord.Thread):
            return
        if before.content == after.content and before.attachments == after.attachments:
            return

        docs = (
            db.collection("tickets")
            .where("channel_id", "==", after.channel.id)
            .limit(1)
            .get()
        )

        if not docs:
            return

        ticket_name = docs[0].id

        await log_ticket_message_event(
            self.bot,
            ticket_name,
            (
                f"✏️ {after.author.display_name} edited a message\n"
                f"Before: {before.content or '*empty*'}\n"
                f"After: {after.content or '*empty*'}"
            ),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
