import discord

from economy.gamba.coinflip_choice_view import CoinChoiceView


class CoinflipAcceptView(discord.ui.View):
    def __init__(self, challenger, opponent):
        super().__init__(timeout=300)

        self.challenger = challenger
        self.opponent = opponent

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button):

        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "You are not the one being challenged.",
                ephemeral=True,
            )
            return

        view = CoinChoiceView(
            challenger=self.challenger,
            opponent=self.opponent,
        )

        embed = discord.Embed(
            title="<:oathcoin:1462999179998531614> Coinflip",
            description=f"{self.opponent.mention}, choose **Heads** or **Tails**.",
            color=discord.Color.gold(),
        )

        embed.add_field(
            name="Players",
            value=f"{self.challenger.mention} vs {self.opponent.mention}",
            inline=False,
        )

        await interaction.response.edit_message(
            embed=embed,
            view=view,
        )

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button):

        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "You are not the one being challenged.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="❌ Coinflip Declined",
            description=f"{self.opponent.mention} declined the challenge.",
            color=discord.Color.gold(),
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None,
        )
