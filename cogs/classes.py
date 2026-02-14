import discord
from discord import app_commands
from discord.ext import commands

from class_setups.boss_setup_view import BossSetupView
from class_setups.embed_class import build_class_embed
from class_setups.utils import (
    _normalize,
    build_class_index,
    clear_class_index,
    clear_sheet_cache,
    get_class_image,
    get_class_index,
    get_class_loadouts,
    get_classes_for_boss,
)
from config import BOSS_TO_SHEET, BOSS_TYPES, DISCORD_MANAGER_ROLE_ID


class ClassSetups(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 🔎 AUTOCOMPLETE
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

    # 🔥 CLASS COMMAND
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

        await build_class_index()

        index = get_class_index()  # alias → canonical
        loadouts = get_class_loadouts()  # canonical → loadout

        normalized = _normalize(class_name)
        canonical = index.get(normalized)

        if not canonical:
            return await interaction.followup.send("❌ Class not found.")

        class_data = loadouts[canonical]

        image_url = get_class_image(canonical)

        embed = build_class_embed(
            class_name=canonical,
            general_loadout=class_data,
            consumables=class_data,
            image_url=image_url,
        )

        view = BossSetupView(
            class_name=canonical,  # pass canonical name to buttons
            boss_types=BOSS_TYPES,
            boss_sheets=BOSS_TO_SHEET,
        )

        await interaction.followup.send(embed=embed, view=view)

    # 🔥 BOSS COMMAND
    @app_commands.command(
        name="boss",
        description="Show all class loadouts for a boss",
    )
    async def boss_loadouts(
        self,
        interaction: discord.Interaction,
        boss: str,
    ):
        await interaction.response.defer()

        try:
            data = await get_classes_for_boss(boss)
        except ValueError:
            return await interaction.followup.send("❌ Unknown boss.")

        if not data:
            return await interaction.followup.send("No loadouts found.")

        embed = discord.Embed(
            title=f"{boss.title()} Loadouts",
            color=discord.Color.blurple(),
        )

        for class_name, loadout in list(data.items())[:10]:
            embed.add_field(
                name=class_name,
                value=(
                    f"<:swordaqw:1457810578994233434> {loadout.get('sword', '—')}\n"
                    f"<:helmaqw:1457810605443383307> {loadout.get('helm', '—')}\n"
                    f"<:cloakaqw:1457810628168253522> {loadout.get('cloak', '—')}"
                ),
                inline=False,
            )

        image_url = "https://pbs.twimg.com/media/DQ4C_sSV4AAwHqo.jpg"
        if image_url:
            embed.set_thumbnail(url=image_url)

        await interaction.followup.send(embed=embed)

    # 🔄 RECACHE
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
