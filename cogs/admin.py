import sys

import discord
from discord import app_commands
from discord.ext import commands

from startup import run_startup_tasks


# 🔒 Optional: restrict to bot owner(s)
def is_owner():
    async def predicate(interaction: discord.Interaction) -> bool:
        app = await interaction.client.application_info()
        return interaction.user.id == app.owner.id

    return app_commands.check(predicate)


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="reload",
        description="Reload a cog",
    )
    @app_commands.describe(cog="Name of the cog (e.g. profile, tickets, admin)")
    @is_owner()
    async def reload(self, interaction: discord.Interaction, cog: str):
        await interaction.response.defer(ephemeral=True)

        ext = f"cogs.{cog}"

        try:
            await self.bot.reload_extension(ext)
            await self.bot.tree.sync()
            await run_startup_tasks(self.bot)

            await interaction.followup.send(
                f"✅ Reloaded `{ext}` successfully.",
                ephemeral=True,
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to reload `{ext}`:\n```{type(e).__name__}: {e}```",
                ephemeral=True,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
