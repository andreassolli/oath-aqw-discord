from discord.ext import commands

from ticket_help import setup_ticket_system
from ticket_help.commands.admin import (
    add_boss,
    adjust_points,
    delete_boss,
    delete_type,
    lookup_points,
    reload_point_rules,
    remove_claimer,
    reset_all_points,
    set_boss_points,
    set_user_points,
)


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._started: bool = False  # ✅ type-safe, cog-local state

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

    @commands.Cog.listener()
    async def on_ready(self):
        # Prevent double-start on reload / reconnect
        if self._started:
            return

        self._started = True
        await setup_ticket_system(self.bot)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
