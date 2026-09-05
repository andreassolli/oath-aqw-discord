import discord
from discord import app_commands
from discord.ext import commands
from io import BytesIO

from class_setups.boss_setup_view import BossSetupView
from class_setups.embed_class import ClassView
from class_setups.utils import (
    _normalize,
    build_class_index,
    clear_class_index,
    clear_sheet_cache,
    get_class_across_bosses,
    get_class_image,
    get_class_index,
    get_class_loadouts,
    get_classes_for_boss,
)
from config import (
    ALLOWED_COMMANDS_CHANNELS,
    DISCORD_MANAGER_ROLE_ID,
)


class ClassSetups(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def class_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ):

        normalized_current = _normalize(current)
        loadouts = get_class_loadouts()

        matches = [
            app_commands.Choice(
                name=canonical,
                value=canonical,
            )
            for canonical in loadouts.keys()
            if normalized_current in _normalize(canonical)
        ][:25]

        return matches

    @app_commands.command(
        name="class",
        description="Show class setups and boss-specific loadouts",
    )
    @app_commands.autocomplete(class_name=class_autocomplete)
    async def class_loadouts(
        self,
        interaction: discord.Interaction,
        class_name: str,
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

        await build_class_index()

        index = get_class_index()
        loadouts = get_class_loadouts()

        normalized = _normalize(class_name)
        canonical = index.get(normalized)

        if not canonical:
            return await interaction.followup.send(
                "❌ Class not found."
            )

        class_data = loadouts[canonical]

        # Get every boss this class appears in
        boss_loadouts = await get_class_across_bosses(canonical)

        # Get cached image
        class_image = get_class_image(canonical)

        view = ClassView(
            class_name=canonical,
            general_loadout=class_data,
            consumables=class_data,
            class_image=class_image,
            boss_loadouts=boss_loadouts,
        )

        if view.class_file:
            await interaction.followup.send(
                view=view,
                file=view.class_file,
            )
        else:
            await interaction.followup.send(
                view=view,
            )


    @app_commands.command(
        name="recache-loadouts",
        description="Force refresh loadout and image cache",
    )
    @app_commands.checks.has_role(DISCORD_MANAGER_ROLE_ID)
    async def recache_loadouts(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        clear_sheet_cache()
        clear_class_index()
        await build_class_index()

        await interaction.followup.send(
            "🔄 Loadout and image cache cleared.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ClassSetups(bot))
