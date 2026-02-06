import discord
from firebase_admin import firestore
from firebase_client import db

async def build_leaderboard_embed(guild: discord.Guild):
    users = (
        db.collection("users")
        .order_by("points", direction=firestore.Query.DESCENDING)
        .limit(10)
        .stream()
    )

    medals = ["🥇", "🥈", "🥉"]
    lines = []

    for i, user_doc in enumerate(users):
        data = user_doc.to_dict()

        user_id = int(user_doc.id)
        member = guild.get_member(user_id)
        display_name = (
            member.display_name
            if member
            else data.get("username", f"User {user_id}")
        )

        name = f"{display_name}"

        points = data.get("points", 0)
        tickets = data.get("tickets_claimed", 0)

        medal = medals[i] if i < 3 else "•"

        lines.append(
            f"{medal} {name} — **{points} pts**"
        )

    if not lines:
        return discord.Embed(
            title="🏆 Ticket Leaderboard",
            description="No ticket data yet.",
            color=discord.Color.gold()
        )

    embed = discord.Embed(
        title="🏆 Ticket Leaderboard",
        description="\n".join(lines),
        color=discord.Color.gold()
    )

    embed.set_footer(text="Points are awarded by ticket complexity. Can't see yourself or someone you know on the leaderboard? Use the command `/lookup user` for the users points you want to see.")
    return embed
