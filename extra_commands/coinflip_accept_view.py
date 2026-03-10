import discord

from extra_commands.coinflip_choice_view import CoinChoiceView


class CoinflipAcceptView(discord.ui.View):
    def __init__(self, challenger, opponent):
        super().__init__(timeout=60)

        self.challenger = challenger
        self.opponent = opponent

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button):

        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "You are not the challenged player.",
                ephemeral=True,
            )
            return

        view = CoinChoiceView(
            challenger=self.challenger,
            opponent=self.opponent,
        )

        await interaction.response.edit_message(
            content=f"{self.opponent.mention}, choose **Heads** or **Tails**.",
            view=view,
        )

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button):

        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "You are not the challenged player.",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(
            content="❌ Challenge declined.",
            view=None,
        )
