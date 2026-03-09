import discord


def build_verification_log_embed(
    *,
    guild: discord.Guild,
    discord_id: int,
    ign: str,
    aqw_username: str | None = None,
    previous_igns: list[str],
    guild_name: str,
    denied: bool = False,
):
    member = guild.get_member(discord_id)

    display = member.display_name if member else f"User {discord_id}"

    if denied:
        title = "❌ Denied Join Application"
    else:
        title = "🛡️ AQW Verification Complete"

    embed = discord.Embed(
        title=title,
        color=discord.Color.green() if not denied else discord.Color.red(),
        timestamp=discord.utils.utcnow(),
    )
    if aqw_username:
        previous_igns.append(aqw_username)
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
