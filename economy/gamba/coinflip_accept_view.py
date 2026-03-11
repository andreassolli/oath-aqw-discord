import discord

from economy.gamba.coinflip_choice_view import CoinChoiceView
from firebase_client import db


class CoinflipAcceptView(discord.ui.View):
    def __init__(self, challenger, opponent, wager: int):
        super().__init__(timeout=300)

        self.challenger = challenger
        self.opponent = opponent
        self.wager = wager

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button):

        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "You are not the one being challenged.",
                ephemeral=True,
            )
            return

        user_ref = db.collection("users").document(str(self.opponent.id))
        doc = user_ref.get()

        coins = doc.to_dict().get("coins", 0) if doc else 0

        if coins < self.wager:
            return await interaction.response.send_message(
                f"You don't have enough coins to accept this wager ({self.wager}).",
                ephemeral=True,
            )

        view = CoinChoiceView(
            challenger=self.challenger,
            opponent=self.opponent,
            wager=self.wager,
        )

        embed = discord.Embed(
            title="<:oathcoin:1462999179998531614> Coinflip",
            description=f"{self.opponent.mention}, choose **Heads** or **Tails**.",
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="Wager",
            value=f"<:oathcoin:1462999179998531614> {self.wager}",
            inline=False,
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
