import discord


def build_points_log_embed(
    *,
    guild: discord.Guild,
    target: discord.Member,
    moderator: discord.Member,
    before: int,
    after: int,
):
    delta = after - before

    if delta > 0:
        title = "💰 Points Added"
        color = discord.Color.green()
    elif delta < 0:
        title = "💸 Points Removed"
        color = discord.Color.red()
    else:
        title = "💰 Points Adjusted"
        color = discord.Color.blurple()

    embed = discord.Embed(
        title=title,
        color=color,
        timestamp=discord.utils.utcnow(),
    )

    embed.add_field(
        name="User",
        value=f"{target.mention}\n`{target.id}`",
        inline=True,
    )

    embed.add_field(
        name="Moderator",
        value=moderator.mention,
        inline=True,
    )

    embed.add_field(
        name="Change",
        value=f"{before} → {after} (**{delta:+}** pts)",
        inline=False,
    )

    return embed
