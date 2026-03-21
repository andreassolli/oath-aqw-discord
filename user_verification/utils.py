import asyncio
import re
from datetime import datetime
from typing import Dict, TypedDict
from urllib.parse import parse_qs

import discord

from config import (
    CCID_PAGE,
    HELPER_ROLE_ID,
    INITIATE_ROLE_ID,
    PROXY_SERVICE,
    STRANGER_ROLE_ID,
    UNSWORN_ROLE_ID,
)
from http_client import get_session

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://account.aq.com/CharPage",
}


class AQWProfile(TypedDict):
    ccid: str
    guild: str | None
    level: int


async def fetch_aqw_profile(username: str) -> AQWProfile | None:
    url = f"{CCID_PAGE}{username}"

    session = await get_session()

    async with session.get(url, headers=HEADERS, proxy=PROXY_SERVICE) as resp:
        text = await resp.text()

    data = parse_qs(text.lstrip("&"))

    char_id = data.get("CharID", [None])[0]
    if char_id is None:
        return None

    level_field = data.get("intLevel", [""])[0]

    guild: str | None = None
    level = 0

    if "---" in level_field:
        level_str, guild = level_field.split(" --- ", 1)
        level = int(level_str)

        guild = guild.strip()

        if guild.endswith(" Guild"):
            guild = guild.removesuffix(" Guild")

        if not guild:
            guild = None
    else:
        level = int(level_field)

    return {
        "ccid": char_id,
        "level": level,
        "guild": guild,
    }


def check_for_bot_badges(badges: list[dict]) -> Dict[str, bool]:
    moosefish = any(badge.get("sTitle") == "Derp Moosefish" for badge in badges)
    mad_bro = any(badge.get("sTitle") == "You mad bro?" for badge in badges)

    return {
        "moosefish": moosefish,
        "mad_bro": mad_bro,
    }


async def change_roles(
    member: discord.Member,
    *,
    is_join_event: bool,
    verified_guild: str | None = None,
    verified_at_all: bool = True,
) -> bool:
    initiate_role = discord.utils.get(member.guild.roles, id=INITIATE_ROLE_ID)
    stranger_role = discord.utils.get(member.guild.roles, id=STRANGER_ROLE_ID)
    unsworn_role = discord.utils.get(member.guild.roles, id=UNSWORN_ROLE_ID)
    helper_role = discord.utils.get(member.guild.roles, id=HELPER_ROLE_ID)
    try:
        if not verified_at_all:
            await member.remove_roles(
                initiate_role,
                unsworn_role,
                helper_role,
                reason="User isnt verified",
            )
            await member.add_roles(
                stranger_role,
                reason="User isnt verified",
            )
            return True
        # 1️⃣ User joined guild
        if is_join_event:
            await member.remove_roles(
                stranger_role,
                unsworn_role,
                reason="User joined Oath",
            )
            await member.add_roles(
                initiate_role,
                helper_role,
                reason="User joined Oath",
            )
            return True

        # 2️⃣ Verified and belongs to Oath
        if verified_guild == "Oath":
            # If they previously had Initiate → scenario 3

            # Normal verification inside guild → scenario 2
            await member.remove_roles(
                stranger_role,
                unsworn_role,
                reason="User verified in Oath",
            )
            await member.add_roles(
                initiate_role,
                helper_role,
                reason="User verified in Oath",
            )
            return True

        # 4️⃣ Verified but not in Oath
        await member.remove_roles(
            stranger_role,
            initiate_role,
            reason="User verified outside Oath",
        )
        await member.add_roles(
            unsworn_role,
            helper_role,
            reason="User verified outside Oath",
        )
        return True

    except Exception as e:
        print(f"Error assigning roles: {e}")
        return False


def build_join_ticket_embed(
    *,
    guild: discord.Guild,
    discord_id: int,
    ign: str,
    created_at: datetime | None = None,
):
    member = guild.get_member(discord_id)

    embed = discord.Embed(
        title="🎮 Guild Join Request",
        description=f"{member.mention if member else f'<@{discord_id}>'} wants to join **Oath**",
        color=discord.Color.blue(),
        timestamp=created_at or discord.utils.utcnow(),
    )

    embed.add_field(name="IGN", value=ign, inline=True)
    embed.add_field(
        name="Discord User",
        value=member.display_name if member else f"User {discord_id}",
        inline=True,
    )

    embed.add_field(
        name="Instructions",
        value=(
            "1. Invite this player to Oath in-game\n"
            "2. Once they have joined, close this ticket\n"
            "3. The bot will verify their guild automatically"
        ),
        inline=False,
    )

    return embed
