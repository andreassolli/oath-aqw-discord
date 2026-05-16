import discord

SPEAKER_OPTIONS = {
    "DPS": "CSH, VDK, Guardian ++",
    "Lord of Order": "",
    "Legion Revenant": "",
    "ArchPaladin": "",
    "Fill": "Cover what is left",
}

SPEAKER_ROLE_EMOJIS = {
    "DPS": "⚔️",
    "Lord of Order": "⚖️",
    "Legion Revenant": "💀",
    "ArchPaladin": "🛡️",
    "Fill": "➕",
}

GRIM_OPTIONS = {
    "DPS": "CSH, GT, Guardian",
    "Sub DPS": "AF, LC, Arachnomancer",
    "Support": "Lord of Order",
    "Healer": "LH, SC, FB, DMoM, GW",
    "Taunter 1": "Verus DoomKnight",
    "Taunter 2": "Legion Revenant",
    "Tank": "ArchPaladin",
    "Fill": "Cover what is left",
}

GRIM_ROLE_EMOJIS = {
    "DPS": "⚔️",
    "Sub DPS": "🗡️",
    "Support": "⚖️",
    "Healer": "⛑️",
    "Taunter 1": "📜",
    "Taunter 2": "📜",
    "Tank": "🛡️",
    "Fill": "➕",
}


class RoleModal(discord.ui.Modal, title="Role Selection"):
    def __init__(self, roles: dict[str, str], boss: str):
        super().__init__()
        if boss == "Grim":
            OPTIONS = GRIM_OPTIONS
            ROLE_EMOJIS = GRIM_ROLE_EMOJIS
        else:
            OPTIONS = SPEAKER_OPTIONS
            ROLE_EMOJIS = SPEAKER_ROLE_EMOJIS

        taken_roles = set(roles.values())

        available = []
        taken = []

        for role, desc in OPTIONS.items():
            option = discord.SelectOption(
                label=f"{ROLE_EMOJIS.get(role, '❔')} {role}",
                value=role,
                description=desc,
                emoji="🔒" if role in taken_roles and role != "Fill" else None,
            )

            (taken if role in taken_roles else available).append(option)

        options = available + taken
        self.role_selection = discord.ui.Label(
            text="Select a role", component=discord.ui.Select(options=options)
        )
        self.add_item(self.role_selection)

    async def on_submit(self, interaction: discord.Interaction):
        role = self.role_selection.component.values[0]
        await interaction.response.send_message(f"You selected: {role}", ephemeral=True)
