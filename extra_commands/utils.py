import random
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Literal

import discord
from discord import app_commands
from google.cloud.firestore import ArrayUnion

from config import (
    ANNOUNCEMENT_CHANNEL_ID,
    BANNED_LIST_CHANNEL_ID,
    EVENT_CHANNEL_ID,
    INITIATE_ROLE_ID,
    LEADERBOARD_HISTORY_CHANNEL_ID,
    LORE_CHANNEL_ID,
    OATH_EVENT_CHANNEL_ID,
    OATHSWORN_ROLE_ID,
    OFFICER_CHANNEL_ID,
    OG_SAN_ID,
    POTW_ROLE_ID,
    POTW_THREAD_ID,
)
from firebase_client import db
from user_profile.utils import fetch_badges


def normalize_filename(name: str | None) -> str | None:
    if not name:
        return None
    return name.strip().lower()


async def send_winner_embed(
    interaction: discord.Interaction,
    user: discord.Member,
    title: str,
    message: str,
    where: Literal["All", "Oath"],
):
    channel_id = OATH_EVENT_CHANNEL_ID if where == "Oath" else EVENT_CHANNEL_ID
    guild = interaction.guild
    if not guild:
        raise RuntimeError("Guild not found")
    channel = guild.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        raise RuntimeError("Event channel is not a text channel")
    embed = discord.Embed(
        title=title,
        description=f"{user.mention} {message}",
        color=discord.Color.green(),
    )
    await channel.send(embed=embed)


def has_any_role(*role_ids: int):
    async def predicate(interaction: discord.Interaction) -> bool:
        user_role_ids = [role.id for role in interaction.user.roles]
        return any(role_id in user_role_ids for role_id in role_ids)

    return app_commands.check(predicate)


MAX_BADGES_TO_DISPLAY = 40
MAX_DESCRIPTION_LENGTH = 4000


async def check_missing_badges(user: discord.Member) -> discord.Embed:
    user_ref = db.collection("users").document(str(user.id))
    doc = user_ref.get()

    ccid = doc.to_dict().get("ccid") if doc.exists else None
    if not ccid:
        return discord.Embed(
            title="Missing Badges",
            description="❌ No CCID linked to this user.",
            color=discord.Color.red(),
        )

    badges = await fetch_badges(ccid)

    api_titles = {
        normalize_filename(b["sFileName"]) for b in badges if b.get("sFileName")
    }

    metadata_doc = db.collection("badge_metadata").document("all").get()

    if not metadata_doc.exists:
        return discord.Embed(
            title="Missing Badges",
            description="⚠ Badge metadata not synced yet.",
            color=discord.Color.orange(),
        )

    badge_map = metadata_doc.to_dict()["badges"]

    missing_badges = []

    for filename, data in badge_map.items():
        filename = normalize_filename(filename)
        if filename == normalize_filename("charbadge-17thBirthdayCollection.jpg"):
            filename = normalize_filename("charbadge-17thBirthdayCollection2.jpg")
        if filename == normalize_filename("charbadge-eternaldragonchest.png"):
            filename = normalize_filename("charbadge-eternaldragonchest.jpg")
        if filename == normalize_filename("charbadge-2022calendar.jpg"):
            filename = normalize_filename("charbadge-2022calendar2.jpg")
        if data["is_pseudo_rare"] and data["is_heromart"]:
            continue
        if filename not in api_titles and not data["is_rare"]:
            missing_badges.append(data)

    total_missing = len(missing_badges)

    if total_missing == 0:
        return discord.Embed(
            title="Missing Badges",
            description=f"✅ {user.display_name} has all non-rare badges!",
            color=discord.Color.green(),
        )

    # If too many badges → summary only
    if total_missing > MAX_BADGES_TO_DISPLAY:
        pseudo_badges = [b for b in missing_badges if b.get("is_pseudo_rare")]
        heromart_badges = [b for b in missing_badges if b.get("is_heromart")]
        special_badges = [b for b in missing_badges if b.get("is_special_offer")]

        def format_category(badges, emoji, label):
            count = len(badges)

            if count == 0:
                return f"{emoji} {label}: 0"

            if count == 1:
                name = badges[0].get("name", "Unknown Badge")
                return f"{emoji} {label}: **{name}**"

            return f"{emoji} {label}: {count}"

        description = (
            "Too many badges to display individually.\n\n"
            + format_category(pseudo_badges, "⚠️", "Pseudo Rare")
            + "\n"
            + format_category(heromart_badges, "🛒", "HeroMart")
            + "\n"
            + format_category(special_badges, "🎁", "Special Offer")
            + "\n\nDisclaimer: HeroMart badges may be rare!"
        )

        embed = discord.Embed(
            title=f"Missing Badges ({total_missing})",
            description=description,
            color=discord.Color.orange(),
        )

        embed.set_footer(text=f"User: {user.display_name}")
        return embed

    description_lines = []
    current_length = 0
    cut_off = False

    description_lines.append("Pseudo Rare: ⚠️\n")
    description_lines.append("HeroMart: 🛒\n")
    description_lines.append("Special Offer: 🎁\n\n")
    description_lines.append("Disclaimer: HeroMart badges may be rare!\n")

    for badge in sorted(missing_badges, key=lambda x: x["name"] or ""):
        name = badge["name"] or "Unknown Badge"
        requirements = badge.get("requirements") or "No requirements listed."

        emojis = ""
        if badge.get("is_pseudo_rare"):
            emojis += " ⚠️"
        if badge.get("is_heromart"):
            emojis += " 🛒"
        if badge.get("is_special_offer"):
            emojis += " 🎁"

        block = f"• **{name}**{emojis}\n↳ {requirements}\n\n"

        if current_length + len(block) > MAX_DESCRIPTION_LENGTH:
            cut_off = True
            break

        description_lines.append(block)
        current_length += len(block)

    description = "".join(description_lines)

    if cut_off:
        description += "⚠ Output truncated due to Discord limits.\n"

    embed = discord.Embed(
        title=f"Missing Badges ({total_missing})",
        description=description,
        color=discord.Color.blurple(),
    )

    embed.set_footer(text=f"User: {user.display_name}")

    return embed


def is_ban_channel():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.channel_id != BANNED_LIST_CHANNEL_ID:
            await interaction.response.send_message(
                "❌ This command can only be used in the designated moderation channel.",
                ephemeral=True,
            )
            return False
        return True

    return app_commands.check(predicate)


async def create_potw_poll(channel: discord.TextChannel):
    guild = channel.guild

    nominees_doc = db.collection("meta").document("potw_nominees").get()

    if nominees_doc.exists:
        options = nominees_doc.to_dict().get("nominees", [])
    else:
        options = []

    if not options:
        await channel.send("No nominees available.")
        return

    poll_duration = timedelta(days=1)

    poll = discord.Poll(
        question="🗳️ Vote for the Player of the Week!",
        duration=poll_duration,
    )

    for user_id in options:
        member = guild.get_member(int(user_id))
        if member:
            poll.add_answer(text=member.display_name)

    embed = discord.Embed(
        title="🗳️ Player of the Week Poll",
        description="Vote for this week's Player of the Week!",
        color=discord.Color.blue(),
    )

    embed.set_footer(text="Poll ends in 24 hours")

    message = await channel.send(embed=embed, poll=poll)

    db.collection("meta").document("potw_poll").set(
        {
            "message_id": message.id,
            "channel_id": channel.id,
            "ends_at": datetime.now(UTC) + poll_duration,
        }
    )

    return message


async def elect_potw(member: discord.Member):

    guild = member.guild

    potw_role = guild.get_role(POTW_ROLE_ID)

    if not potw_role:
        return

    for m in potw_role.members:
        await m.remove_roles(potw_role)

    await member.add_roles(potw_role)

    now = datetime.now(UTC)

    week_of_month = (now.day - 1) // 7 + 1

    month_name = now.strftime("%B")

    user_ref = db.collection("users").document(str(member.id))

    potw_entry = {
        "year": now.year,
        "month": now.month,
        "week": week_of_month,
        "timestamp": int(now.timestamp()),
    }

    user_ref.set(
        {
            "has_been_potw": True,
            "potw_history": ArrayUnion([potw_entry]),
        },
        merge=True,
    )

    #
    # Build embed
    #
    embed = discord.Embed(
        title="🏆 Player of the Week",
        description=f"{month_name} {now.year} Week {week_of_month}\n{member.mention}",
        color=discord.Color.gold(),
        timestamp=now,
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    thread = guild.get_channel(POTW_THREAD_ID)

    if thread is None:
        try:
            thread = await guild.fetch_channel(POTW_THREAD_ID)
        except discord.NotFound:
            print("POTW thread not found")
            return

    if isinstance(thread, discord.Thread):
        await thread.send(embed=embed)
    else:
        print("Channel is not a thread")

    announcement_channel = guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    initiate_role = guild.get_role(INITIATE_ROLE_ID)
    if announcement_channel and initiate_role:
        message = (
            f"{initiate_role.mention}\n"
            f"👑 A new Player of the Week has been crowned:\n"
            f"**{member.mention}**\n\n"
            f"We recognize their great contributions to Oath!<:oath:1457451850184917122>\n\n"
            f"Make sure to say hi if you see them in-game, "
            f"and spam them with lots of pings on Discord!"
            f"<:GoobHeart:1459836996381048863>"
        )

        await announcement_channel.send(message)


def format_duration(total_days):
    years = total_days // 365
    remaining_days = total_days % 365

    months = remaining_days // 30
    days = remaining_days % 30

    parts = []

    if years:
        if years == 1:
            parts.append(f"{years} year")
        else:
            parts.append(f"{years} years")
    if months:
        if months == 1:
            parts.append(f"{months} month")
        else:
            parts.append(f"{months} months")
    if days or not parts:
        if days == 1:
            parts.append(f"{days} day")
        elif days:
            parts.append(f"{days} days")

    return " ".join(parts)


async def elect_potw_by_name(username: str, guild: discord.Guild):

    potw_role = guild.get_role(POTW_ROLE_ID)

    if not potw_role:
        return

    for member in potw_role.members:
        await member.remove_roles(potw_role)

    member = discord.utils.find(
        lambda m: m.display_name == username or m.name == username,
        guild.members,
    )

    if not member:
        return

    #
    # Assign role
    #
    await member.add_roles(potw_role)

    now = datetime.now(UTC)

    week_of_month = (now.day - 1) // 7 + 1

    month_name = now.strftime("%B")

    user_ref = db.collection("users").document(str(member.id))

    potw_entry = {
        "year": now.year,
        "month": now.month,
        "week": week_of_month,
        "timestamp": int(now.timestamp()),
    }

    user_ref.set(
        {
            "has_been_potw": True,
            "potw_history": ArrayUnion([potw_entry]),
        },
        merge=True,
    )

    officer_channel = guild.get_channel(OFFICER_CHANNEL_ID)

    if isinstance(officer_channel, discord.TextChannel):
        await officer_channel.send(
            f"🎉 {member.mention} has been elected Player of the Week!"
        )

    embed = discord.Embed(
        title="🏆 Player of the Week",
        description=f"{month_name} {now.year} Week {week_of_month}\n{member.mention}",
        color=discord.Color.gold(),
        timestamp=now,
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    thread = guild.get_channel(POTW_THREAD_ID)

    if thread is None:
        thread = await guild.fetch_channel(POTW_THREAD_ID)

    if isinstance(thread, discord.Thread):
        await thread.send(embed=embed)


async def manual_leaderboard_post(interaction: discord.Interaction):
    guild = interaction.guild
    if not guild:
        return

    channel = guild.get_channel(LEADERBOARD_HISTORY_CHANNEL_ID)
    if channel is None:
        channel = await guild.fetch_channel(LEADERBOARD_HISTORY_CHANNEL_ID)
    users = {
        "Aidest": 2187,
        "Fird": 1870,
        "OG San": 1430,
        "Samdal": 1348,
        "AxelAnimations": 511,
        "Paboloso": 477,
        "Muhr So": 450,
        "Z e ta": 359,
        "L1ght0": 336,
        "Bookworm": 336,
        "Quincy Dao": 320,
        "Krydoom": 308,
        "cyore": 307,
        "Maou": 301,
        "Proxy": 268,
    }
    medals = ["🥇", "🥈", "🥉"]
    lines = []

    for i, (display_name, points) in enumerate(users.items()):
        position = i + 1
        guild = "💠 Oath"
        if display_name == "AxelAnimations":
            guild = "On Gouache"
        elif display_name == "NEGGS":
            guild = "Vanaheim"
        elif display_name == "cyore":
            guild = "LunchBox"

        if i < 3:
            prefix = medals[i]
        else:
            prefix = f"`{position:02}`"

        lines.append(f"{prefix} **{display_name}** `{guild}` — `{points}` points")

    embed = discord.Embed(
        title="🏆 Leaderboard for April 2026 (Top 15)",
        description="\n".join(lines),
        color=discord.Color.gold(),
        timestamp=datetime.now(UTC),
    )
    if isinstance(channel, discord.Thread):
        await channel.send(embed=embed)


def is_oath_or_allowed_user():
    async def predicate(interaction: discord.Interaction) -> bool:

        # Allow specific user
        if interaction.user.id == OG_SAN_ID:
            return True

        # Allow users with OATHSWORN role
        return any(role.id == OATHSWORN_ROLE_ID for role in interaction.user.roles)

    return app_commands.check(predicate)


async def count_messages(channel: discord.TextChannel):
    counts = defaultdict(int)

    async for message in channel.history(limit=None):
        if message.author.bot:
            continue

        counts[str(message.author.id)] += 1

    return counts


def update_message_counts(counts: dict):
    batch = db.batch()
    batch_size = 0

    for user_id, count in counts.items():
        ref = db.collection("users").document(user_id)

        batch.set(
            ref,
            {"message_count": count},
            merge=True,
        )

        batch_size += 1

        if batch_size == 400:
            batch.commit()
            batch = db.batch()
            batch_size = 0

    if batch_size > 0:
        batch.commit()


async def process_channel(channel: discord.TextChannel):
    counts = await count_messages(channel)
    update_message_counts(counts)
