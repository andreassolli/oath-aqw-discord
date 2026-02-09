import discord
from config import (
    ADMIN_ROLE_ID,
    DISCORD_MANAGER_ROLE_ID,
    HELPER_ROLE_ID,
    OATHSWORN_ROLE_ID,
)

ADMIN_LIKE_ROLES = {ADMIN_ROLE_ID, DISCORD_MANAGER_ROLE_ID}


def has_admin_role(interaction: discord.Interaction) -> bool:
    if not interaction.guild or not interaction.user:
        return False

    return any(role.id in ADMIN_LIKE_ROLES for role in interaction.user.roles)


def has_helper_role(interaction: discord.Interaction) -> bool:
    if not interaction.guild or not interaction.user:
        return False

    return any(role.id == HELPER_ROLE_ID for role in interaction.user.roles)


def has_oathsworn_role(interaction: discord.Interaction) -> bool:
    if not interaction.guild or not interaction.user:
        return False

    return any(role.id == OATHSWORN_ROLE_ID for role in interaction.user.roles)
