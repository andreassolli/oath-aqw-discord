import discord

from quests.utils import get_frequent_quests, get_weekly_quests

EMOTE_TYPE_MAP = {
    "Helm": "<:helmaqw:1487000474014974054>",
    "Armor": "<:armoraqw:1487000736087670936>",
    "Weapon": "<:swordaqw:1487004634307629056>",
    "Cape": "<:cloakaqw:1457810628168253522>",
    "Polearm": "<:spearaqw:1487000575290642553>",
    "Axe": "<:axeaqw:1487000523268947988>",
    "Class": "<:classbadge:1471256107057156117>",
    "Dagger": "<:daggeraqw:1487000631653961779>",
    "Whip": "🌀",
    "Gun": "<:revolveraqw:1491412344411127958>",
    "HandGun": "<:revolveraqw:1491412344411127958>",
    "Rifle": "<:rifleaqw:1491412383200051201>",
    "Bow": "<:bowaqw:1487000684204265533>",
    "Pet": "<:petaqw:1491408513124008088>",
    "House": "🏠",
    "Floor Item": "🪑",
    "Wall Item": "🖼️",
    "Item": "🦴",
    "Misc": "🕳️",
    "Quest Item": "🔮",
    "Mace": "<:maceaqw:1491408562231181353>",
    "Staff": "🪄",
    "Gauntlet": "<:gauntletaqw:1487000801695109160>",
}


def format_quest_block(quest_id: str, items: list) -> str:
    lines = [f"**<:queststart:1491012167170920560> {quest_id.upper()}**"]

    for item in items:
        lines.append(
            f"{EMOTE_TYPE_MAP.get(item['strType'], '🦴')} {item['strName']} ({item['strType']})"
        )

    return "\n".join(lines)


async def build_static_quest_embed() -> discord.Embed:
    weekly_quests = await get_weekly_quests()
    frequent_quests = await get_frequent_quests()

    description_parts = []

    for quest_id, items in weekly_quests.items():
        block = format_quest_block(quest_id, items)
        description_parts.append(block)

    description_parts.append("---")

    for quest_id, items in frequent_quests.items():
        block = format_quest_block(quest_id, items)
        description_parts.append(block)

    if not description_parts:
        description = "No quests available right now."
    else:
        description = (
            "Each Weekly Quest rewards <:oathcoin:1462999179998531614>1000, while the Frequent Quests rewards <:oathcoin:1462999179998531614>150.\n\n"
            "\n\n".join(description_parts)
        )

    embed = discord.Embed(
        title="📜 Available Quests", description=description, color=discord.Color.gold()
    )

    return embed
