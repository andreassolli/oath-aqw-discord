import discord

from economy.gamba.coinflip_choice_view import CoinChoiceView
from economy.gamba.utils import lock_coins, unlock_coins
from firebase_client import db


class CoinflipAcceptView(discord.ui.View):
    def __init__(self, challenger, opponent, wager: int):
        super().__init__(timeout=300)

        self.challenger = challenger
        self.opponent = opponent
        self.wager = wager
        self.message: discord.InteractionMessage | None = None
        self.resolved = False

    async def on_timeout(self):
        if self.resolved:
            return

        self.resolved = True

        unlock_coins(self.challenger.id, self.wager)

        for child in self.children:
            child.disabled = True

        if self.message:
            try:
                await self.message.edit(
                    content="⌛ Coinflip challenge timed out. Coins refunded.",
                    view=self,
                )
            except Exception:
                pass

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button):

        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "You are not the one being challenged.",
                ephemeral=True,
            )
            return

        # ✅ lock opponent coins (handles validation too)
        success, error = lock_coins(self.opponent.id, self.wager)

        if not success:
            return await interaction.response.send_message(
                error,
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

        # ✅ prevent timeout + further interaction
        self.resolved = True

        for child in self.children:
            child.disabled = True

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

        if self.resolved:
            return

        self.resolved = True

        unlock_coins(self.challenger.id, self.wager)

        embed = discord.Embed(
            title="❌ Coinflip Declined",
            description=f"{self.opponent.mention} declined the challenge.",
            color=discord.Color.gold(),
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None,
        )
