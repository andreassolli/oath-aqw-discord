from typing import Dict, List

import discord

from economy.utils import ShopItem


async def shop_embed(items: List[ShopItem]):
    embed = discord.Embed(
        title="Shop",
        description="These are the items currently available for purchase.",
        color=discord.Color.magenta(),
    )

    for item in items:
        embed.add_field(
            name=item["name"],
            value=f"<:oathcoin:1462999179998531614>{item['price']}",
            inline=False,
        )

    embed.set_footer(text="Use `/buy <item>` to buy an item from the shop.")
    return embed
