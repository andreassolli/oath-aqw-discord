from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from google.cloud import firestore

from firebase_client import db
from quests.setup_quests import setup_quests


class Quests(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="quests-add", description="Add item to this weeks quest."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def quests_add(
        self,
        interaction: discord.Interaction,
        quest: Literal["Weekly 1", "Weekly 2", "Frequent 1", "Frequent 2"],
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
        await interaction.response.defer(ephemeral=True)
        if quest == "Weekly 1":
            quest_ref = db.collection("weekly-quests").document("quest1")
        elif quest == "Weekly 2":
            quest_ref = db.collection("weekly-quests").document("quest2")
        elif quest == "Frequent 1":
            quest_ref = db.collection("frequent-quests").document("quest1")
        else:
            quest_ref = db.collection("frequent-quests").document("quest2")

        quest_ref.collection("items").add({"name": item_name, "type": item_type})
        await setup_quests(self.bot)
        await interaction.followup.send(
            f"Added {item_name} to quest {quest}.", ephemeral=True
        )

    @app_commands.command(name="quests-view", description="View items for this quest.")
    @app_commands.default_permissions(manage_guild=True)
    async def quests_view(
        self,
        interaction: discord.Interaction,
        quest: Literal["Weekly 1", "Weekly 2", "Frequent 1", "Frequent 2"],
    ):
        await interaction.response.defer(ephemeral=True)
        if quest == "Weekly 1":
            quest_ref = db.collection("weekly-quests").document("quest1")
        elif quest == "Weekly 2":
            quest_ref = db.collection("weekly-quests").document("quest2")
        elif quest == "Frequent 1":
            quest_ref = db.collection("frequent-quests").document("quest1")
        else:
            quest_ref = db.collection("frequent-quests").document("quest2")

        items = quest_ref.collection("items").stream()
        items_list = [doc.to_dict().get("name") for doc in items]
        if not items_list:
            await interaction.followup.send(
                f"Quest {quest} has no items.", ephemeral=True
            )
            return
        await interaction.followup.send(
            f"Quest {quest} items: {', '.join([item.get('name') for item in items_list])}",
            ephemeral=True,
        )

    @app_commands.command(name="quests-remove", description="Remove item from quest.")
    @app_commands.default_permissions(manage_guild=True)
    async def quests_remove(
        self,
        interaction: discord.Interaction,
        quest: Literal["Weekly 1", "Weekly 2", "Frequent 1", "Frequent 2"],
        item_name: str,
    ):
        await interaction.response.defer(ephemeral=True)
        if quest == "Weekly 1":
            quest_ref = db.collection("weekly-quests").document("quest1")
        elif quest == "Weekly 2":
            quest_ref = db.collection("weekly-quests").document("quest2")
        elif quest == "Frequent 1":
            quest_ref = db.collection("frequent-quests").document("quest1")
        else:
            quest_ref = db.collection("frequent-quests").document("quest2")

        items = quest_ref.collection("items").where("name", "==", item_name).stream()

        found = False
        for doc in items:
            doc.reference.delete()
            found = True

        if found:
            await interaction.followup.send(
                f"Removed {item_name} from quest {quest}.", ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"Quest {quest} has no item named {item_name}.", ephemeral=True
            )

    @app_commands.command(
        name="frequents-reset", description="Remove Frequent quests from all users."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def frequents_reset(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        users_ref = db.collection("users")
        docs = users_ref.stream()

        batch = db.batch()
        batch_count = 0
        BATCH_LIMIT = 500

        updated = 0

        for doc in docs:
            user_data = doc.to_dict() or {}
            quests = user_data.get("quests_completed", [])

            # Skip users who don't have these quests
            if "Frequent 1" not in quests and "Frequent 2" not in quests:
                continue

            batch.update(
                doc.reference,
                {
                    "quests_completed": firestore.ArrayRemove(
                        ["Frequent 1", "Frequent 2"]
                    )
                },
            )

            batch_count += 1
            updated += 1

            # 🚀 Commit every 500 writes
            if batch_count >= BATCH_LIMIT:
                batch.commit()
                batch = db.batch()
                batch_count = 0

        # Final commit
        if batch_count > 0:
            batch.commit()

        await interaction.followup.send(
            f"✅ Removed Frequent quests from {updated} users.", ephemeral=True
        )

    @app_commands.command(
        name="weeklies-reset", description="Remove Weekly quests from all users."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def weeklies_reset(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        users_ref = db.collection("users")
        docs = users_ref.stream()

        batch = db.batch()
        batch_count = 0
        BATCH_LIMIT = 500

        updated = 0

        for doc in docs:
            user_data = doc.to_dict() or {}
            quests = user_data.get("quests_completed", [])

            # Skip users who don't have these quests
            if "Weekly 1" not in quests and "Weekly 2" not in quests:
                continue

            batch.update(
                doc.reference,
                {"quests_completed": firestore.ArrayRemove(["Weekly 1", "Weekly 2"])},
            )

            batch_count += 1
            updated += 1

            # 🚀 Commit every 500 writes
            if batch_count >= BATCH_LIMIT:
                batch.commit()
                batch = db.batch()
                batch_count = 0

        # Final commit
        if batch_count > 0:
            batch.commit()

        await interaction.followup.send(
            f"✅ Removed Weekly quests from {updated} users.", ephemeral=True
        )

    @app_commands.command(
        name="weeklies-clear", description="Clear all items from this weeks quest."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def weeklies_clear(
        self,
        interaction: discord.Interaction,
        quest: Literal["Weekly 1", "Weekly 2", "Frequent 1", "Frequent 2"],
    ):
        await interaction.response.defer(ephemeral=True)

        items = (
            db.collection("weekly-quests")
            .document(f"quest{quest}")
            .collection("items")
            .get()
        )
        if not items:
            await interaction.followup.send(
                f"Quest {quest} has no items.", ephemeral=True
            )
            return
        for item in items:
            db.collection("weekly-quests").document(f"quest{quest}").collection(
                "items"
            ).document(item.id).delete()

        await setup_quests(self.bot)
        await interaction.followup.send(
            f"Cleared all items from quest {quest}.", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Quests(bot))
