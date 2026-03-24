import discord

from economy.gamba.utils import lock_coins, unlock_coins
from economy.gamba.yanken_choice_view import RPSChoiceView
from firebase_client import db


class RPSAcceptView(discord.ui.View):
    def __init__(self, challenger, opponent, wager):
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
                    content="⌛ Challenge timed out. Coins refunded.", view=self
                )
            except:
                pass

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button):

        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "You are not the challenged player.",
                ephemeral=True,
            )
            return

        success, error = lock_coins(self.opponent.id, self.wager)

        if not success:
            return await interaction.response.send_message(error, ephemeral=True)

        view = RPSChoiceView(
            challenger=self.challenger,
            opponent=self.opponent,
            wager=self.wager,
        )

        embed = discord.Embed(
            title="<:gon:1480922691950088293> Rock Paper Scissors",
            description=f"Wager: <:oathcoin:1462999179998531614> {self.wager}\nBoth players choose your move.",
            color=discord.Color.orange(),
        )
        embed.set_thumbnail(
            url="https://preview.redd.it/do-you-think-gon-could-have-beaten-neferpitou-without-v0-1f9xqd69c62f1.jpeg?auto=webp&s=23512378c9a247701ac04bb96d60663130e3e51d"
        )
        try:
            self.resolved = True

            for child in self.children:
                child.disabled = True

            await interaction.response.edit_message(embed=embed, view=view)

        except Exception:
            # rollback opponent lock if something fails
            unlock_coins(self.opponent.id, self.wager)
            raise

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button):

        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "You are not the challenged player.",
                ephemeral=True,
            )
            return

        if self.resolved:
            return

        self.resolved = True
        unlock_coins(self.challenger.id, self.wager)
        await interaction.response.edit_message(
            content="❌ Challenge declined.",
            view=None,
        )
