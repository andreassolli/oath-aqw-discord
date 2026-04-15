import discord

from extra_commands.record_utils import (
    build_leaderboard,
    get_most_claimed,
    get_most_coins,
    get_most_counts,
    get_most_points,
)
from firebase_client import db


async def record_holder(board_type: str) -> discord.Embed:
    config = {
        "points": (get_most_points, "total_points", "🏆 Points Leaderboard"),
        "counts": (get_most_counts, "counting_score", "🎲 Counting Leaderboard"),
        "claimed": (get_most_claimed, "total_claimed", "🔖 Claimed Leaderboard"),
        "coins": (
            get_most_coins,
            "coins",
            "<:oathcoin:1462999179998531614> Coins Leaderboard",
        ),
    }

    if board_type not in config:
        raise ValueError("Invalid leaderboard type")

    fetch_func, field, title = config[board_type]

    users_ref = await fetch_func()
    lines = await build_leaderboard(users_ref, field)

    description = "\n".join(lines) if lines else "No data available."

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.gold(),
    )

    return embed
