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

    medals = ["<:rule1w:1505157671836454972>", "<:rule2w:1505157669995151381>", "<:rule3w:1505157669017751592>", "<:rule4w:1505157667893543033>", "<:rule5w:1505157666740375632>"]
    lines = []

    for i, doc in enumerate(users):
        data = doc.to_dict() or {}

        position = i + 1
        member = guild.get_member(int(doc.id))

        display_name = (
            member.display_name if member else data.get("aqw_username", "Unknown User")
        )

        points = data.get("points", 0)

        if i < 5:
            prefix = "<:leftwing:1505157673249935402>" + medals[i] + "<:rightwing:1505157674776531015>"
        else:
            prefix = f"`{position:02}`"
        aqw_guild = data.get("guild", "")
        if aqw_guild and aqw_guild != "None":
            if aqw_guild == "Oath":
                guild_str = " <:oath:1457451850184917122> `Oath` "
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
        color=discord.Colour(7344907),
    )

    embed.set_footer(
        text="Points are awarded by ticket complexity. Can't see yourself? Use `/profile user`."
    )

    return embed

class LeaderboardView(discord.ui.LayoutView):
    def __init__(self, guild: discord.Guild):

        super().__init__(timeout=None)

        users = (
            db.collection("users")
            .order_by("points", direction="DESCENDING")
            .where("verified", "==", True)
            .limit(25)
            .stream()
        )

        medals = ["<:rule1w:1505157671836454972>", "<:rule2w:1505157669995151381>", "<:rule3w:1505157669017751592>", "<:rule4w:1505157667893543033>", "<:rule5w:1505157666740375632>"]
        lines = []

        for i, doc in enumerate(users):
            data = doc.to_dict() or {}

            position = i + 1
            member = guild.get_member(int(doc.id))

            display_name = (
                member.display_name if member else data.get("aqw_username", "Unknown User")
            )

            points = data.get("points", 0)

            if i < 5:
                prefix = "<:leftwing:1505157673249935402>" + medals[i] + "<:rightwing:1505157674776531015>"
            else:
                prefix = f"`{position:02}`"
            aqw_guild = data.get("guild", "")
            if aqw_guild and aqw_guild != "None":
                if aqw_guild == "Oath":
                    guild_str = " <:oath:1457451850184917122> `Oath` "
                else:
                    guild_str = f"`{aqw_guild}` "
            else:
                guild_str = ""
            if i == 15:
                lines.append("\n----------CUTOFF FOR LORE POST----------\n")
            lines.append(f"{prefix} **{display_name}** {guild_str}— `{points}` points")

        self.container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/leaderboardoath.webp",
                ),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:medal:1505158451179819119>** Ticket Leaderboard** (Top 25)"
            ),
            discord.ui.TextDisplay(
                content=(
                    f">>> {"\n".join(lines)}"
                )
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="*Points are awarded by ticket complexity. Can't see yourself? Use `/profile user`.*"
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bright_separator.png",
                ),
            ),
            accent_colour=discord.Colour(7344907),
        )

        self.add_item(self.container1)
