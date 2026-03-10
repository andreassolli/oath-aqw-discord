import discord

from economy.gamba.utils import coinflip


class CoinChoiceView(discord.ui.View):
    def __init__(self, challenger, opponent):
        super().__init__(timeout=300)

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

        heads_coin = "<:goobCoin:1480895675477524564>"
        tails_coin = "<:oathcoin:1462999179998531614>"
        coin = heads_coin if result.lower() == "heads" else tails_coin

        embed = discord.Embed(
            title=f"{tails_coin} Coinflip Result",
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="Choice",
            value=f"{self.opponent.mention} chose **{opponent_choice.capitalize()}**",
            inline=False,
        )

        embed.add_field(
            name="Result",
            value=f"{coin} **{result.capitalize()}**",
            inline=False,
        )

        embed.add_field(
            name="Winner",
            value=f"🏆 {winner.mention}",
            inline=False,
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None,
        )
