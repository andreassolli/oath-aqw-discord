import discord


class ChangeBossModal(discord.ui.Modal, title="Change Bosses"):
    def __init__(self, bosses: list[str], current: list[str]):
        super().__init__()

        options = []
        for boss in bosses:
            option = discord.CheckboxGroupOption(
                label=boss, value=boss, default=boss in current
            )
            options.append(option)

        self.boss_selection = discord.ui.Label(
            text="Select the bosses for this ticket",
            component=discord.ui.CheckboxGroup(
                options=options,
                required=True,
            ),
        )
        self.add_item(self.boss_selection)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Current bosses: {', '.join(self.boss_selection.component.values)}",
            ephemeral=True,
        )
