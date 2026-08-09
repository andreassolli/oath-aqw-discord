from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from quests.new_quests import ChangeQuestModal
from firebase_client import db

class Quests(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="quest-stats",
        description="View quest completion statistics.",
    )
    async def quest_stats(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ):
        await interaction.response.defer()

        target = user or interaction.user

        user_doc = db.collection("users").document(str(target.id)).get()

        if not user_doc.exists:
            return await interaction.followup.send(
                "❌ That user doesn't have a profile yet.",
                ephemeral=True,
            )

        data = user_doc.to_dict() or {}

        completed = data.get("quests_completed", [])
        total_completed = data.get("quests_completed_count", 0)

        all_quests = [
            "Weekly 1",
            "Weekly 2",
            "Frequent 1",
            "Frequent 2",
        ]

        remaining = [q for q in all_quests if q not in completed]

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Quest Stats <:queststart:1491012167170920560>",
            description=f"\n<:misc:1532256591141929031> Total Quests Completed:`{total_completed}`\n\n<:aqwcheck:1532278320870326382> **Current Quests Completed**\n{"\n".join(f"> {q}" for q in completed)}{"\n\n<:scroll:1532256096063062157> Remaining\n" if len(remaining) > 0 else ""}{"\n".join(f"> {q}" for q in remaining)}",
            color=discord.Colour(7344907),
        )

        embed.set_footer(
            text=f"{len(completed)}/{len(all_quests)} current quests completed"
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="change-quests",
        description="Replace the items for a quest.",
    )
    async def change_quests(
        self,
        interaction: discord.Interaction,
        quest: Literal["Weekly 1", "Weekly 2", "Frequent 1", "Frequent 2"],
    ):
        if quest == "Weekly 1":
            quest_ref = db.collection("weekly-quests").document("quest1")
        elif quest == "Weekly 2":
            quest_ref = db.collection("weekly-quests").document("quest2")
        elif quest == "Frequent 1":
            quest_ref = db.collection("frequent-quests").document("quest1")
        else:
            quest_ref = db.collection("frequent-quests").document("quest2")

        await interaction.response.send_modal(
            ChangeQuestModal(self.bot, quest_ref, quest)
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Quests(bot))
