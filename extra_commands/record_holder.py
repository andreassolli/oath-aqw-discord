import discord

from extra_commands.record_utils import (
    build_leaderboard,
    get_highest_level,
    get_most_claimed,
    get_most_coins,
    get_most_counts,
    get_most_points,
)
from firebase_client import db


async def record_holder(board_type: str, guild: discord.Guild) -> discord.Embed:
    config = {
        "points": (get_most_points, "total_points", "🏆 Gathered the most points"),
        "counts": (get_most_counts, "counting_score", "🎲 Counted the most"),
        "claimed": (
            get_most_claimed,
            "total_claimed",
            "🔖 Helped the most amount of tickets",
        ),
        "coins": (
            get_most_coins,
            "coins",
            "<:oathcoin:1462999179998531614> Most amount of coins",
        ),
        "level": (get_highest_level, "level", "📊 Highest Level"),
    }

    if board_type not in config:
        raise ValueError("Invalid leaderboard type")

    fetch_func, field, title = config[board_type]

    users_ref = fetch_func()
    lines = await build_leaderboard(users_ref, field, guild)

    description = "\n".join(lines) if lines else "No data available."

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.gold(),
    )

    return embed
