from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from firebase_client import db


class Forge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="weeklies-add", description="Add item to this weeks quest."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def weeklies_add(
        self,
        interaction: discord.Interaction,
        quest: Literal[1, 2],
        item_name: str,
        item_type: Literal[
            "Axe",
            "Dagger",
            "Sword",
            "Mace",
            "Staff",
            "Gun",
            "Polearm",
            "Bow",
            "Rifle",
            "Gauntlet",
            "HandGun",
            "Whip",
            "Armor",
            "Class",
            "Cape",
            "Helm",
            "Pet",
            "Quest Item",
            "Item",
            "Misc",
            "Wall Item",
            "House",
            "Floor Item",
        ],
    ):
        db.collection("weekly-quests").document(f"quest{quest}").collection(
            "items"
        ).add({"name": item_name, "type": item_type})
        await interaction.response.send_message(
            f"Added {item_name} to quest {quest}.", ephemeral=True
        )

    @app_commands.command(
        name="weeklies-view", description="Add item to this weeks quest."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def weeklies_view(
        self,
        interaction: discord.Interaction,
        quest: Literal[1, 2],
    ):
        items = (
            db.collection("weekly-quests")
            .document(f"quest{quest}")
            .collection("items")
            .get()
        )
        if not items:
            await interaction.response.send_message(
                f"Quest {quest} has no items.", ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"Quest {quest} items: {', '.join([item.get('name') for item in items])}",
            ephemeral=True,
        )

    @app_commands.command(
        name="weeklies-remove", description="Remove item from this weeks quest."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def weeklies_remove(
        self,
        interaction: discord.Interaction,
        quest: Literal[1, 2],
        item_name: str,
    ):
        items = (
            db.collection("weekly-quests")
            .document(f"quest{quest}")
            .collection("items")
            .get()
        )
        if not items:
            await interaction.response.send_message(
                f"Quest {quest} has no items.", ephemeral=True
            )
            return
        for item in items:
            if item.get("name") == item_name:
                db.collection("weekly-quests").document(f"quest{quest}").collection(
                    "items"
                ).document(item.id).delete()
                await interaction.response.send_message(
                    f"Removed {item_name} from quest {quest}.", ephemeral=True
                )
                return
        await interaction.response.send_message(
            f"Quest {quest} has no item named {item_name}.", ephemeral=True
        )

    @app_commands.command(
        name="weeklies-clear", description="Clear all items from this weeks quest."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def weeklies_clear(
        self,
        interaction: discord.Interaction,
        quest: Literal[1, 2],
    ):
        items = (
            db.collection("weekly-quests")
            .document(f"quest{quest}")
            .collection("items")
            .get()
        )
        if not items:
            await interaction.response.send_message(
                f"Quest {quest} has no items.", ephemeral=True
            )
            return
        for item in items:
            db.collection("weekly-quests").document(f"quest{quest}").collection(
                "items"
            ).document(item.id).delete()
        await interaction.response.send_message(
            f"Cleared all items from quest {quest}.", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Forge(bot))
