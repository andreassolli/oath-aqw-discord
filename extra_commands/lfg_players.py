import discord


class LFGPlayersLayout(discord.ui.LayoutView):
    def __init__(self, users):
        self.users = users
        super().__init__()
        items: list[discord.ui.Item] = [
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/loltourney.png",
                ),
            ),
            discord.ui.TextDisplay(content="‎"),
        ]

        users_string = "\n".join(
            [f"<@{user.user_id}> ({user.display_name})" for user in users]
        )
        items.append(
            discord.ui.TextDisplay(
                content=(
                    f"<:hands:1505158458494681138> **Players without team**\n>>> {users_string}"
                ),
            ),
        )

        items.append(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bright_separator.png",
                ),
            )
        )

        self.container = discord.ui.Container(
            *items,
            accent_colour=discord.Colour(7344907),
        )

        self.add_item(self.container)
