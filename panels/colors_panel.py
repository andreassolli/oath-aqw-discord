import discord

from config import (
    CELESTIAL_ROLE_ID,
    COLOR_ROLES,
    CRIMSON_FLAME_ROLE_ID,
    VERDANT_ROLE_ID,
    VOID_ROLE_ID,
)


class RoleButton(discord.ui.Button):
    def __init__(self, label, role_id):
        self.role_id = role_id
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f"role_{role_id}",
        )

    async def callback(self, interaction: discord.Interaction):
        await handle_role_toggle(interaction, self.role_id)


class RoleLayout(discord.ui.LayoutView):
    container1 = discord.ui.Container(
        discord.ui.TextDisplay(content="**Choose Your Color Role**"),
        discord.ui.TextDisplay(
            content="All members can claim one of these base colors to make your name stand out:"
        ),
        discord.ui.Separator(visible=False),
        discord.ui.TextDisplay(content=f"<@&{VERDANT_ROLE_ID}>"),
        discord.ui.Section(
            discord.ui.TextDisplay(content="> Embrace natures verdant color."),
            accessory=RoleButton(
                label="🌱 Verdant",
                role_id=VERDANT_ROLE_ID,
            ),
        ),
        discord.ui.TextDisplay(content=f"<@&{CRIMSON_FLAME_ROLE_ID}>"),
        discord.ui.Section(
            discord.ui.TextDisplay(content="> Engulf yourself in crimson flames."),
            accessory=RoleButton(
                label="🔥 Crimson Flame",
                role_id=CRIMSON_FLAME_ROLE_ID,
            ),
        ),
        discord.ui.TextDisplay(content=f"<@&{VOID_ROLE_ID}>"),
        discord.ui.Section(
            discord.ui.TextDisplay(content="> Slip into the void, slowly."),
            accessory=RoleButton(
                label="🔮 Void",
                role_id=VOID_ROLE_ID,
            ),
        ),
        discord.ui.TextDisplay(content=f"<@&{CELESTIAL_ROLE_ID}>"),
        discord.ui.Section(
            discord.ui.TextDisplay(content="> To the skies and beyond."),
            accessory=RoleButton(
                label="🪽 Celestial",
                role_id=CELESTIAL_ROLE_ID,
            ),
        ),
        discord.ui.Separator(visible=False),
        discord.ui.TextDisplay(
            content="Boost the server to unlock extra colors, including exclusive gradient options!"
        ),
    )


async def handle_role_toggle(
    interaction: discord.Interaction,
    role_id: int,
):
    guild = interaction.guild
    user = interaction.user

    if guild is None or not isinstance(user, discord.Member):
        return

    target_role = guild.get_role(role_id)
    if target_role is None:
        await interaction.response.send_message(
            "Role configuration error. Please contact an admin.",
            ephemeral=True,
        )
        return

    if target_role in user.roles:
        await user.remove_roles(target_role)
        await interaction.response.send_message(
            f":negative_squared_cross_mark: Removed role <@&{role_id}>", ephemeral=True
        )
        return

    roles_to_remove = [r for r in user.roles if r.id in COLOR_ROLES]
    if roles_to_remove:
        await user.remove_roles(*roles_to_remove)
        await user.add_roles(target_role)
        await interaction.response.send_message(
            f":arrows_counterclockwise: Changed role to {target_role.mention}",
            ephemeral=True,
        )
        return

    await user.add_roles(target_role)
    await interaction.response.send_message(
        f":white_check_mark: Added role <@&{role_id}>", ephemeral=True
    )
