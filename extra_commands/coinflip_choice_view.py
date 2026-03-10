import discord

from extra_commands.utils import coinflip


class CoinChoiceView(discord.ui.View):
    def __init__(self, challenger, opponent):
        super().__init__(timeout=60)

        self.challenger = challenger
        self.opponent = opponent

    @discord.ui.button(label="Heads", style=discord.ButtonStyle.primary)
    async def heads(self, interaction: discord.Interaction, button):
        await self.resolve(interaction, "Heads")

    @discord.ui.button(label="Tails", style=discord.ButtonStyle.primary)
    async def tails(self, interaction: discord.Interaction, button):
        await self.resolve(interaction, "Tails")

    async def resolve(self, interaction: discord.Interaction, opponent_choice: str):

        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "You are not the opponent.", ephemeral=True
            )
            return

        result = await coinflip(fair=True)

        challenger_wins = result == opponent_choice
        winner = self.opponent if challenger_wins else self.challenger

        await interaction.response.edit_message(
            content=(
                f"<:oathcoin:1462999179998531614> Coin landed on **{result.capitalize()}**\n"
                f"{self.opponent.mention} chose **{opponent_choice.capitalize()}**\n\n"
                f"🏆 {winner.mention} wins!"
            ),
            view=None,
        )
