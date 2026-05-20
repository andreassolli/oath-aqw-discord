import asyncio
import time
from datetime import timedelta
from typing import Any, Dict, cast

import discord

from config import (
    BADGES,
    GAMBA_UPDATES_CHANNEL_ID,
    SPAM_CMD_CHANNEL_ID,
    TICKET_LOG_CHANNEL_ID,
)
from firebase_client import db
from quests.utils import check_for_quest_completion


async def setup_quests(client: discord.Client):
    channel = client.get_channel(GAMBA_UPDATES_CHANNEL_ID)

    if not channel:
        print("❌ Ticket panel channel not found. Check TICKET_CHANNEL_ID.")
        return

    async for msg in channel.history(limit=3):
        if msg.author == client.user:
            await msg.delete()

    await channel.send(view=QuestsLayout())


class QuestsLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        self.container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/quests.png",
                ),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164>** What are quests?**"
            ),
            discord.ui.TextDisplay(
                content=">>> <a:sparks:1505157330055069706> Quests are a way to earn coins to use for discord stuff like profile background, among other things.\nEach Weekly Quest rewards <:oathcoin:1462999179998531614>1000, while the Sporadic Quests rewards <:oathcoin:1462999179998531614>150."
            ),
            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large,
            ),
            discord.ui.TextDisplay(
                content="<:queststart:1491012167170920560> **Weekly Quest 1**"
            ),
            discord.ui.TextDisplay(
                content=">>> <:aqwDagger:1487000631653961779> Brutal Sword and Shield<:tagAC:1498781113127145482>\n<:aqwGauntlet:1487000801695109160> Brutal Sword and Shield Gauntlet<:tagAC:1498781113127145482>\n🗽 Enraged Undead Warrior Guard<:tagAC:1498781113127145482>\n🗽 Undead Warrior Guard<:tagAC:1498781113127145482>"
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:queststart:1491012167170920560> **Weekly Quest 2**"
            ),
            discord.ui.TextDisplay(
                content=">>> <:aqwClass:1501670684101840906> Dark Lord Class<:tagAC:1498781113127145482><:tagSeasonal:1498781292689625158>"
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:queststart:1491012167170920560> **Sporadic Quest 1**"
            ),
            discord.ui.TextDisplay(
                content=">>> 🗽 Discarded Combat Droid Guard<:tagAC:1498781113127145482><:tagSeasonal:1498781292689625158>\n🗽 Standalonian Combat Droid<:tagAC:1498781113127145482><:tagRare:1498781237777535126>\n🗽 Standalonian Droid<:tagAC:1498781113127145482><:tagSeasonal:1498781292689625158>"
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:queststart:1491012167170920560> **Sporadic Quest 2**"
            ),
            discord.ui.TextDisplay(
                content=">>> 🪄 Earth Mother's Gift<:tagAC:1498781113127145482><:tagSeasonal:1498781292689625158>\n🪄 Apatura Iris<:tagAC:1498781113127145482><:tagSeasonal:1498781292689625158>"
            ),
            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large,
            ),
            discord.ui.TextDisplay(
                content="<:queststart:1491012167170920560> **Gathered the required items?**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=">>> Click '**Check Inventory**' to see if you have the required items. Remember to keep the items in your inventory when checking!"
                ),
                accessory=QuestCheckButton(),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bright_separator.png",
                ),
            ),
            accent_colour=discord.Colour(7344907),
        )
        self.add_item(self.container1)


class QuestCheckButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="🧳 Check Inventory",
            style=discord.ButtonStyle.secondary,
            custom_id="quest_check_button",
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if not interaction.guild:
            return await interaction.followup.send(
                "This can only be used in a server.", ephemeral=True
            )

        user_id = interaction.user.id

        result = await check_for_quest_completion(user_id)

        await interaction.followup.send(
            result,
            ephemeral=True,
        )
