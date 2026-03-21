import discord

from firebase_client import db


async def build_leaderboard_embed(guild: discord.Guild):
    users = (
        db.collection("users")
        .order_by("points", direction="DESCENDING")
        .where("verified", "==", True)
        .limit(25)
        .stream()
    )

    medals = ["🥇", "🥈", "🥉"]
    lines = []

    for i, doc in enumerate(users):
        data = doc.to_dict() or {}

        position = i + 1
        member = guild.get_member(int(doc.id))

        display_name = (
            member.display_name if member else data.get("aqw_username", "Unknown User")
        )

        points = data.get("points", 0)

        if i < 3:
            prefix = medals[i]
        else:
            prefix = f"`{position:02}`"
        aqw_guild = data.get("guild", "")
        if aqw_guild != "None" or aqw_guild != "":
            if aqw_guild == "Oath":
                guild_str = "`💠Oath` "
            else:
                guild_str = f"`{aqw_guild}` "
        else:
            guild_str = ""
        if i == 15:
            lines.append("\n----------CUTOFF FOR LORE POST----------\n")
        lines.append(f"{prefix} **{display_name}** {guild_str}— `{points}` points")

    if not lines:
        return discord.Embed(
            title="🏆 Ticket Leaderboard (Top 25)",
            description="No ticket data yet.",
            color=discord.Color.gold(),
        )

    embed = discord.Embed(
        title="🏆 Ticket Leaderboard (Top 25)",
        description="\n".join(lines),
        color=discord.Color.gold(),
    )

    embed.set_footer(
        text="Points are awarded by ticket complexity. Can't see yourself? Use `/profile user`."
    )

    return embed
