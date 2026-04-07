import discord

from quests.utils import get_quests

EMOTE_TYPE_MAP = {
    "Helm": "<:helmaqw:1487000474014974054>",
    "Armor": "<:armorqw:1487000474014974054>",
    "Weapon": "<:swordaqw:1487004634307629056>",
    "Cape": "<:cloakaqw:1457810628168253522>",
    "Polearm": "<:spearaqw:1487000575290642553>",
    "Axe": "<:axeaqw:1487000523268947988>",
    "Class": "<:classbadge:1471256107057156117>",
    "Whip": "🌀",
    "Gun": "🔫",
    "HandGun": "🔫",
    "Rifle": "🔫",
    "Bow": "🏹",
    "Pet": "🐾",
    "House": "🏠",
    "Floor Item": "🪑",
    "Wall Item": "🖼️",
    "Item": "🦴",
    "Misc": "🕳️",
    "Quest Item": "🔮",
    "Mace": "🔨",
    "Staff": "🪄",
    "Gauntlet": "🥊",
}


def format_quest_block(quest_id: str, items: list) -> str:
    lines = [f"**<:queststart:1491012167170920560> {quest_id.upper()}**"]

    for item in items:
        lines.append(
            f"{EMOTE_TYPE_MAP.get(item['strType'], '🦴')} {item['strName']} ({item['strType']})"
        )

    return "\n".join(lines)


async def build_static_quest_embed() -> discord.Embed:
    quests = await get_quests()

    description_parts = []

    for quest_id, items in quests.items():
        block = format_quest_block(quest_id, items)
        description_parts.append(block)

    description = "\nEach quest rewards <:oathcoin:1462999179998531614>1000.\nOnly available for Beta Testers.\n\n".join(
        description_parts
    )

    embed = discord.Embed(
        title="📜 Available Quests", description=description, color=discord.Color.gold()
    )

    return embed
