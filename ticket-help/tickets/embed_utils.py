import discord
from config import HELPER_ROLE_ID

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
):
    requester_member = guild.get_member(requester_id)
    requester_mention = (
        requester_member.mention
        if requester_member
        else f"<@{requester_id}>"
    )

    # Resolve claimer mentions
    if claimers:
        helpers = "\n".join(
            guild.get_member(uid).mention if guild.get_member(uid) else f"<@{uid}>"
            for uid in claimers
        )
    else:
        helpers = "—"

    helper_role = guild.get_role(HELPER_ROLE_ID)

    role_mention = helper_role.mention

    embed = discord.Embed(
        title=f"🎫 {type} Ticket",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Requester",
        value=requester_mention,
        inline=True
    )

    embed.add_field(
        name="Username",
        value=username,
        inline=True
    )

    embed.add_field(
        name="Server",
        value=f"`{server}`",
        inline=True
    )

    embed.add_field(
        name="Bosses",
        value=", ".join(bosses),
        inline=False
    )

    embed.add_field(
        name="Points",
        value=str(points),
        inline=True
    )

    embed.add_field(
        name="Helpers",
        value=f"{len(claimers)+1} / {max_claims+1}",
        inline=True
    )

    embed.add_field(
        name="Room",
        value=f"`{room}`",
        inline=True
    )

    embed.add_field(
        name="Currently Helping",
        value=helpers,
        inline=False
    )

    embed.set_footer(text=f"Use the buttons below to help!")

    return embed
