from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from quests.new_quests import ChangeQuestModal
from firebase_client import db
from datetime import datetime, timezone

NUMBERS_EMOTES = [
    "<:rule1w:1505157671836454972>",
    "<:rule2w:1505157669995151381>",
    "<:rule3w:1505157669017751592>",
    "<:4wht:1543576731217305690>",
    "<:5wht:1543576732483723345>",
    "<:6wht:1537134850765492305>",
    "<:7wht:1537134853042999306>",
    "<:8wht:1537134854754410597>",
    "<:9wht:1537134856750899240>",
    "<:10wht:1537134858801905795>",
    "<:11wht:1537134860701933668>",
    "<:12wht:1537134862815858728>",
    "<:13wht:1537134864694779974>",
    "<:14wht:1537134866620227685>",
    "<:15wht:1537134868582899833>",
]

GUILD_EMOTES = {
    "Oath": "<:oath:1457451850184917122>",
    "Ravens": "",
    "Solaris": "",
    "Stormforged": "",
    "Vanaheim": "",
}

def formatted_number_emote(num: int):
    if num < 5: return "<:leftwing:1505157673249935402>" + NUMBERS_EMOTES[num] + "<:rightwing:1505157674776531015>"
    return "<:blank:1537132485601665166>" + NUMBERS_EMOTES[num] + "<:blank:1537132485601665166>"

def get_guild(aqw_guild: str):
    return f"{GUILD_EMOTES.get(aqw_guild, "")} `{aqw_guild}`"

class Quests(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command(
        name="quest-leaderboard",
        description="View leaderboard for Quests"
    )
    async def quest_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        docs = (
            db.collection("users")
            .order_by(
                "quest_points",
                direction="DESCENDING"
            )
            .limit(15)
            .stream()
        )

        lines = []

        for i, doc in enumerate(docs):
            data = doc.to_dict() or {}
            member = interaction.guild.get_member(int(doc.id))

            display_name = (
                member.display_name
                if member
                else data.get("aqw_username", "Unknown User")
            )

            aqw_guild = data.get("guild", "")
            quest_points = data.get("quest_points", 0)

            lines.append(
                f"{formatted_number_emote(i)} "
                f"**{display_name}** "
                f"— `{quest_points}` points"
            )

        embed = discord.Embed(
            title="TLAPD Questing Leaderboard <:queststart:1491012167170920560>",
            description=(
                f">>> {"\n".join(lines)}\n\n"
                f"*Can't see yourself? Use `/quest-stats`*"
            ),
            color=discord.Colour(7344907),
        )

        event_end = datetime.fromtimestamp(1789833600, tz=timezone.utc)

        embed.set_footer(
            text=f"Event ends {event_end.strftime('%B %d, %Y at %H:%M UTC')}"
        )

        await interaction.followup.send(embed=embed)

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
        quest_points = data.get("quest_points", 0)

        all_quests = [
            "Weekly 1",
            "Weekly 2",
            "Frequent 1",
            "Frequent 2",
        ]

        remaining = [q for q in all_quests if q not in completed]

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Quest Stats <:queststart:1491012167170920560>",
            description=f"\n🏴‍☠️ TLAPD Questing Points: `{quest_points}`\n<:misc:1532256591141929031> Total Quests Completed:`{total_completed}`\n\n<:aqwcheck:1532278320870326382> **Current Quests Completed**\n{"\n".join(f"> {q}" for q in completed)}{"\n\n<:scroll:1532256096063062157> Remaining\n" if len(remaining) > 0 else ""}{"\n".join(f"> {q}" for q in remaining)}",
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
