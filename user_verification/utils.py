import asyncio
import re
from datetime import datetime
from typing import TypedDict

import discord

from config import AQW_CHAR_PAGE, INITIATE_ROLE_ID, STRANGER_ROLE_ID, UNSWORN_ROLE_ID
from http_client import get_session


class AQWProfile(TypedDict):
    ccid: str
    guild: str


async def fetch_aqw_profile(username: str) -> AQWProfile | None:
    url = f"{AQW_CHAR_PAGE}{username}"

    session = await get_session()

    for attempt in range(3):  # retry up to 3 times
        async with session.get(url) as resp:
            html = await resp.text()

        print(f"{url} : {resp.status}")

        if resp.status == 429:
            print("Rate limited. Waiting before retry...")
            await asyncio.sleep(30)  # wait 30 seconds
            continue

        if resp.status != 200:
            return None

        match_ccid = re.search(r"var\s+ccid\s*=\s*(\d+)\s*;", html)
        if not match_ccid:
            return None

        ccid = match_ccid.group(1)

        match_guild = re.search(r"&amp;guild=([^&]+)", html)
        guild = match_guild.group(1) if match_guild else ""

        return {"ccid": ccid, "guild": guild}

    return None  # after retries


async def change_roles(
    member: discord.Member,
    *,
    is_join_event: bool,
    verified_guild: str | None = None,
) -> bool:
    initiate_role = discord.utils.get(member.guild.roles, id=INITIATE_ROLE_ID)
    stranger_role = discord.utils.get(member.guild.roles, id=STRANGER_ROLE_ID)
    unsworn_role = discord.utils.get(member.guild.roles, id=UNSWORN_ROLE_ID)

    try:
        # 1️⃣ User joined guild
        if is_join_event:
            await member.remove_roles(
                stranger_role,
                unsworn_role,
                reason="User joined Oath",
            )
            await member.add_roles(
                initiate_role,
                reason="User joined Oath",
            )
            return True

        # 2️⃣ Verified and belongs to Oath
        if verified_guild == "Oath":
            # If they previously had Initiate → scenario 3
            if initiate_role in member.roles:
                await member.remove_roles(
                    initiate_role,
                    reason="User re-verified but left Oath",
                )
                await member.add_roles(
                    unsworn_role,
                    reason="User re-verified but not in Oath",
                )
                return True

            # Normal verification inside guild → scenario 2
            await member.remove_roles(
                stranger_role,
                unsworn_role,
                reason="User verified in Oath",
            )
            await member.add_roles(
                initiate_role,
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
