import discord


def build_verification_log_embed(
    *,
    guild: discord.Guild,
    discord_id: int,
    ign: str,
    previous_igns: list[str],
    guild_name: str,
):
    member = guild.get_member(discord_id)

    display = member.display_name if member else f"User {discord_id}"

    embed = discord.Embed(
        title="🛡️ AQW Verification Complete",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow(),
    )

    embed.add_field(name="User", value=display, inline=True)
    embed.add_field(name="IGN", value=ign, inline=True)
    embed.add_field(name="AQW Guild", value=guild_name or "None", inline=True)
    embed.add_field(
        name="Previous IGNs",
        value=", ".join(previous_igns) if previous_igns else "None",
        inline=False,
    )

    embed.set_footer(text=f"Discord ID: {discord_id}")

    return embed
