import discord


class ConfirmModal(discord.ui.Modal, title="Complete Ticket"):
    def __init__(self, bosses: list[str]):
        super().__init__()

        options = []
        for boss in bosses:
            option = discord.CheckboxGroupOption(label=boss, value=boss, default=True)
            options.append(option)

        self.boss_selection = discord.ui.Label(
            text="Completed bosses:",
            component=discord.ui.CheckboxGroup(
                options=options,
                required=True,
            ),
        )
        self.add_item(self.boss_selection)

        self.keep_ticket = discord.ui.Label(
            text="Keep ticket. Choose this if you need to replace helpers",
            component=discord.ui.Checkbox(),
        )
        self.add_item(self.keep_ticket)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Completed: {', '.join(self.boss_selection.component.values[0])}",
            ephemeral=True,
        )
