import discord

ROLE_EMOJIS = {
    "DPS": "⚔️",
    "Sub DPS": "🗡️",
    "Support": "⚖️",
    "Healer": "⛑️",
    "Taunter 1": "📜",
    "Taunter 2": "📜",
    "Tank": "🛡️",
    "Fill": "➕",
    "Lord of Order": "⚖️",
    "ArchPaladin": "🛡️",
    "Legion Revenant": "💀",
}


def build_ticket_embed(
    *,
    requester_id: int,
    bosses: list[str],
    points: int,
    username: str,
    room: str,
    max_claims: int,
    claimers: list[int],
    guild: discord.Guild,
    type: str,
    server: str,
    total_kills: str,
    drops: list[str] = [],
    claimer_roles: dict[str, str] | None = None,
):
    requester_member = guild.get_member(requester_id)
    claimer_roles = claimer_roles or {}
    requester_role = claimer_roles.get(str(requester_id), "Fill")

    # Only apply role formatting in grimchallenge
    if requester_role and ("Grim Challenge" in bosses or "Ultra Speaker" in bosses):
        requester_mention = (
            f"**{ROLE_EMOJIS.get(requester_role, '❔')}{requester_role}:** {requester_member.mention}"
            if requester_member
            else f"**{ROLE_EMOJIS.get(requester_role, '❔')}{requester_role}:** <@{requester_id}>"
        )
    else:
        requester_mention = (
            requester_member.mention if requester_member else f"<@{requester_id}>"
        )

    # Resolve claimer mentions

    if claimers:
        helper_lines = []

        for uid in claimers:
            member = guild.get_member(uid)
            mention = member.mention if member else f"<@{uid}>"

            role = claimer_roles.get(str(uid))

            # Only apply role formatting in grimchallenge
            if role and ("Grim Challenge" in bosses or "Ultra Speaker" in bosses):
                helper_lines.append(
                    f"**{ROLE_EMOJIS.get(role, '❔')}{role}:** {mention}"
                )
            else:
                helper_lines.append(mention)

        helpers = "\n".join(helper_lines)
    else:
        helpers = "—"

    embed = discord.Embed(
        title=f"🎫 {type.capitalize()} Ticket", color=discord.Color.blurple()
    )

    embed.add_field(name="Requester", value=requester_mention, inline=True)

    embed.add_field(name="Username", value=username, inline=True)

    embed.add_field(name="Server", value=f"`{server}`", inline=True)

    embed.add_field(name="Bosses", value=", ".join(bosses), inline=False)

    if type == "spamming":
        embed.add_field(name="Total Kills", value=total_kills, inline=True)

    if type == "until drop":
        embed.add_field(name="Drop Rates", value="%, ".join(drops), inline=True)

    embed.add_field(name="Points", value=str(points), inline=True)

    embed.add_field(
        name="Helpers", value=f"{len(claimers) + 1} / {max_claims + 1}", inline=True
    )

    # if type == "spamming" or type == "testing":
    #    embed.add_field(
    #    name="Room",
    #    value=f"`{room}`",
    #    inline=True
    # )

    embed.add_field(name="Currently Helping", value=helpers, inline=False)

    embed.set_footer(text=f"Use the buttons below to help!")

    return embed
