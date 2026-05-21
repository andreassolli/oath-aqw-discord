import discord


class LeagueTeamsLayout(discord.ui.LayoutView):
    def __init__(self, teams):
        self.teams = teams
        super().__init__()
        items: list[discord.ui.Item] = [
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/loltourney.png",
                ),
            ),
            discord.ui.TextDisplay(content="‎"),
        ]
        slots = [
            "player1",
            "player2",
            "player3",
            "player4",
            "player5",
            "substitute",
        ]

        for team in teams:
            team_data = team.to_dict()

            players = []

            for slot in slots:
                player_id = team_data.get(slot)

                if player_id is not None:
                    players.append(f"<@{player_id}>")

            players_string = "\n".join(players)

            items.append(
                discord.ui.TextDisplay(
                    content=(
                        f"<:id2:1505158104810262558> "
                        f"**{team_data['team_name']}**\n"
                        f">>> {players_string}"
                    ),
                ),
            )
            items.append(discord.ui.TextDisplay(content="‎"))

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
