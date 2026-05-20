import random
import re

import discord
from google.cloud import firestore

from config import GUILD_MEMBERS_COUNT, INITIATE_ROLE_ID, UNSWORN_ROLE_ID
from firebase_client import db


async def process_log(message: discord.Message):
    if not message.embeds or message.embeds[0].title not in {
        "AQW Guild Member(s) Joined",
        "AQW Guild Member(s) Left",
    }:
        return

    guild = message.guild
    if not guild:
        return

    embed = message.embeds[0]
    description = str(embed.description)
    match = re.search(r"Member\(s\):\s*(.+)", description)
    if not match:
        return

    raw_member = match.group(1).split("\n")[0].strip()

    username_match = re.search(r"\[([^\]]+)\]", raw_member)
    username = ""
    if username_match:
        username = username_match.group(1).strip().lower()
        print(username)

    if username == "":
        return

    if embed.title == "AQW Guild Member(s) Joined":
        await update_guild_members_count(guild, join=True)
    elif embed.title == "AQW Guild Member(s) Left":
        await update_guild_members_count(guild, join=False)

    user_query = (
        db.collection("users")
        .where("aqw_username_lower", "==", username)
        .limit(1)
        .get()
    )
    if not user_query:
        return

    user = user_query[0]
    user_ref = user.reference

    if user:
        member = guild.get_member(int(user.id))
        if not member:
            return
        initiate_role = discord.utils.get(member.guild.roles, id=INITIATE_ROLE_ID)
        unsworn_role = discord.utils.get(member.guild.roles, id=UNSWORN_ROLE_ID)
        if (
            embed.title == "AQW Guild Member(s) Joined"
            and initiate_role
            and unsworn_role
        ):
            await member.add_roles(
                initiate_role,
            )
            await member.remove_roles(
                unsworn_role,
            )
            user_ref.update({"guild": "Oath"})

        elif (
            embed.title == "AQW Guild Member(s) Left" and initiate_role and unsworn_role
        ):
            await member.remove_roles(
                initiate_role,
            )
            await member.add_roles(
                unsworn_role,
            )
            user_ref.update({"guild": ""})


async def update_guild_members_count(guild: discord.Guild, join: bool = True):
    channel = guild.get_channel(GUILD_MEMBERS_COUNT)
    channel_name = channel.name if channel else ""
    count = channel_name.split(": ")[1] if channel_name else None
    add = 1 if join else -1
    new_count = int(count) + add if count else 1
    if not channel:
        return
    await channel.edit(name=f"Guild Members: {new_count}")
