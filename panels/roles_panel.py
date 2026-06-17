from typing import TypedDict

import discord

from config import COLOR_ROLE_DATA


class RoleData(TypedDict):
    name: str
    id: int
    subtitle: str
    emoji: str
    emoji_id: int | None


class RoleLayout(discord.ui.LayoutView):
    def __init__(
        self,
        title: str,
        description: str,
        image: str,
        role_data: list[RoleData],
        subtitle: str | None = None,
    ):
        super().__init__(timeout=None)

        components: list[discord.ui.Item] = [
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=f"https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/{image}",
                ),
            ),
            discord.ui.TextDisplay(content=title),
        ]

        # optional subtitle
        if subtitle is not None:
            components.append(discord.ui.TextDisplay(content=subtitle))

        components.append(discord.ui.TextDisplay(content=description))

        components.extend(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"<@&{role['id']}> \n> {role['subtitle']}"
                ),
                accessory=RoleButton(
                    label=role["name"],
                    role_id=role["id"],
                    apply_text=f":white_check_mark: Added role <@&{role['id']}>",
                    remove_text=f":negative_squared_cross_mark: Removed role <@&{role['id']}>",
                    emoji=role["emoji"],
                    custom=role["emoji_id"] is not None,
                ),
            )
            for role in role_data
        )

        container = discord.ui.Container(*components)
        self.add_item(container)


class RoleButton(discord.ui.Button):
    def __init__(
        self,
        label,
        role_id,
        apply_text,
        remove_text,
        emoji,
        emoji_id: int = 0,
        custom: bool = False,
    ):
        self.role_id = role_id
        self.apply_text = apply_text
        self.remove_text = remove_text
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f"role_{role_id}",
            emoji=emoji
            if custom
            else discord.PartialEmoji(
                name=emoji,
                id=emoji_id,
            ),
        )

    async def callback(self, interaction: discord.Interaction):
        await handle_role_toggle(
            interaction, self.role_id, self.apply_text, self.remove_text
        )


async def handle_role_toggle(
    interaction: discord.Interaction,
    role_id: int,
    apply_text: str,
    remove_text: str,
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

    COLOR_ROLE_IDS = [rid for _, rid in COLOR_ROLE_DATA]
    is_color_role = role_id in COLOR_ROLE_IDS

    if target_role in user.roles:
        await user.remove_roles(target_role)
        await interaction.response.send_message(remove_text, ephemeral=True)
        return

    if is_color_role:
        # Only allow one color role at a time
        roles_to_remove = [r for r in user.roles if r.id in COLOR_ROLE_IDS]
        if roles_to_remove:
            await user.remove_roles(*roles_to_remove)
            await user.add_roles(target_role)
            await interaction.response.send_message(
                f":arrows_counterclockwise: Changed role to {target_role.mention}",
                ephemeral=True,
            )
        else:
            await user.add_roles(target_role)
            await interaction.response.send_message(
                apply_text,
                ephemeral=True,
            )
        return
    else:
        # Non-color Roles: just add
        await user.add_roles(target_role)
        await interaction.response.send_message(apply_text, ephemeral=True)
