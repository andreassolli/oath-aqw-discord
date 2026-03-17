import discord

OPTIONS = {
    "DPS": "CSH, GT, Guardian",
    "Sub DPS": "AF, LC, Arachnomancer",
    "Support": "Lord of Order",
    "Healer": "LH, SC, FB, DMoM, GW",
    "Taunter 1": "Verus DoomKnight",
    "Taunter 2": "Legion Revenant",
    "Tank": "ArchPaladin",
    "Fill": "Cover what is left",
}


class RoleSelect(discord.ui.Select):
    def __init__(self, roles: dict[str, str]):
        taken_roles = set(roles.values())

        available = []
        taken = []

        for role, desc in OPTIONS.items():
            option = discord.SelectOption(
                label=role,
                value=role,
                description=desc,
                emoji="🔒" if role in taken_roles else None,
            )

            (taken if role in taken_roles else available).append(option)

        options = available + taken

        super().__init__(
            placeholder="Select a role",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_role = self.values[0]

        await interaction.response.defer()
