import discord

from firebase_client import db


class TeamView(discord.ui.View):
    def __init__(self, teams):
        super().__init__(timeout=60)

        self.add_item(TeamSelect(teams))


class TeamSelect(discord.ui.Select):
    def __init__(self, teams):

        slots = [
            "player1",
            "player2",
            "player3",
            "player4",
            "player5",
            "substitute",
        ]

        options = []

        for team in teams:
            team_data = team.to_dict()

            filled_slots = sum(1 for slot in slots if team_data.get(slot) is not None)

            options.append(
                discord.SelectOption(
                    label=team_data["team_name"],
                    value=team.id,
                    description=f"{filled_slots}/6 players",
                )
            )

        super().__init__(
            placeholder="Select a team",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):

        user = interaction.user
        team_id = self.values[0]

        team_ref = db.collection("league_teams").document(team_id)
        team_doc = team_ref.get()

        if not team_doc.exists:
            await interaction.response.send_message(
                "That team does not exist!", ephemeral=True
            )
            return

        team_data = team_doc.to_dict()

        slots = [
            "player1",
            "player2",
            "player3",
            "player4",
            "player5",
            "substitute",
        ]

        # Prevent duplicate joining
        for slot in slots:
            if team_data.get(slot) == user.id:
                await interaction.response.send_message(
                    f"You are already on {team_data['team_name']}!", ephemeral=True
                )
                return

        # Find empty slot
        for slot in slots:
            if team_data.get(slot) is None:
                team_ref.update({slot: user.id})

                await interaction.response.send_message(
                    f"You joined {team_data['team_name']} as {slot}!"
                )
                return

        await interaction.response.send_message(
            f"{team_data['team_name']} is full!", ephemeral=True
        )
