import discord

from economy.gamba.yanken_choice_view import RPSChoiceView
from firebase_client import db


class RPSAcceptView(discord.ui.View):
    def __init__(self, challenger, opponent, wager):
        super().__init__(timeout=60)

        self.challenger = challenger
        self.opponent = opponent
        self.wager = wager
        self.message: discord.InteractionMessage | None = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button):

        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "You are not the challenged player.",
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

        await interaction.response.edit_message(
            embed=embed,
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
