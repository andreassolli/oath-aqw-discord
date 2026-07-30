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

ITEM_ICONS = {
    "Axe": "<:aqwaxe:1532278309998559382>",
    "Dagger": "<:aqwdagger:1532278336687181934>",
    "Sword": "<:sword:1532256100756361257>",
    "Mace": "<:aqwmace:1532278402482966750>",
    "Staff": "<:aqwstaff:1532278486570369024>",
    "Wand": "<:aqwwand:1532278495156109482>",
    "Gun": "<:aqwgun:1532278392312041603>",
    "Polearm": "<:aqwpolearm:1532278411601514596>",
    "Bow": "<:aqwbow:1532278316630020127>",
    "Rifle": "<:aqwgun:1532278392312041603>",
    "Gauntlet": "<:aqwgauntlet:1532278386141954059>",
    "HandGun": "<:aqwgun:1532278392312041603>",
    "Whip": "<:aqwwhip:1532280038953586748>",
    "Armor": "<:armor:1532256090220138688>",
    "Class": "<:class:1532256037216976916>",
    "Cape": "<:cape:1532256092027879526>",
    "Helm": "<:helm:1532256093881761932>",
    "Pet": "<:pet:1532256098625523722>",
    "Quest Item": "<:scroll:1532256096063062157>",
    "Item": "<:misc:1532256591141929031>",
    "Misc": "<:aqwnecklace:1532278409583919104>",
    "Wall Item": "<:wall:1532255983873818778>",
    "House": "<:aqwhouse:1532278397575893063>",
    "Floor Item": "<:aqwfloor:1532278339233124512>",
}


def build_quest_text(quest_ref) -> str:
    items = [doc.to_dict() for doc in quest_ref.collection("items").stream()]

    if not items:
        return ">>> *No items configured.*"

    lines = []

    for item in items:
        icon = ITEM_ICONS.get(item.get("type"), "<:misc:1532256591141929031>")
        lines.append(f"{icon} {item['name']}")

    return ">>> " + "\n".join(lines)

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

        weekly1 = build_quest_text(
            db.collection("weekly-quests").document("quest1")
        )

        weekly2 = build_quest_text(
            db.collection("weekly-quests").document("quest2")
        )

        frequent1 = build_quest_text(
            db.collection("frequent-quests").document("quest1")
        )

        frequent2 = build_quest_text(
            db.collection("frequent-quests").document("quest2")
        )

        self.container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/quests1.png",
                ),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164>** What are quests?**"
            ),
            discord.ui.TextDisplay(
                content=">>> <a:sparks:1505157330055069706> Quests are a way to earn coins to use for discord stuff like profile background. Each Weekly Quest rewards <:oathcoin:1462999179998531614>1000, while the Sporadic Quests rewards <:oathcoin:1462999179998531614>150."
            ),
            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large,
            ),
            discord.ui.TextDisplay(
                content="<:queststart:1491012167170920560> **Weekly Quest 1**"
            ),
            discord.ui.TextDisplay(content=weekly1),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:queststart:1491012167170920560> **Weekly Quest 2**"
            ),
            discord.ui.TextDisplay(content=weekly2),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:queststart:1491012167170920560> **Sporadic Quest 1**"
            ),
            discord.ui.TextDisplay(content=frequent1),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:queststart:1491012167170920560> **Sporadic Quest 2**"
            ),
            discord.ui.TextDisplay(content=frequent2),
            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large,
            ),
            discord.ui.TextDisplay(
                content="<:aqwcheck:1532278320870326382> **Gathered the required items?**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=">>> Click '**Check Inventory**' to see if you have the required items. Remember to keep the items in your inventory when checking! <:aqwbag:1532278312838103142>"
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
            label="Check Inventory",
            emoji=discord.PartialEmoji(
                name="aqwbag",
                id=1532278312838103142,
            ),
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
