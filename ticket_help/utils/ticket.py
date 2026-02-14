import discord

from config import ADMIN_ROLE_ID, HELPER_ROLE_ID, OATHSWORN_ROLE_ID


def get_overwrites(interaction: discord.Interaction):
    guild = interaction.guild

    base_member_perms = dict(
        view_channel=True,
        send_messages=True,
        read_message_history=True,
        mention_everyone=False,
    )

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(**base_member_perms),
        guild.me: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            mention_everyone=True,
        ),
    }

    role_configs = {
        HELPER_ROLE_ID: base_member_perms,
        OATHSWORN_ROLE_ID: {
            **base_member_perms,
            "mention_everyone": True,
        },
        ADMIN_ROLE_ID: {
            **base_member_perms,
            "mention_everyone": True,
            "manage_channels": True,
        },
    }

    for role_id, perms in role_configs.items():
        role = guild.get_role(role_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(**perms)

    return overwrites
