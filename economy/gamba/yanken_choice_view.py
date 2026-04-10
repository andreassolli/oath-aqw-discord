import discord
from google.cloud import firestore

from economy.gamba.yanken import rock_paper_scissor
from firebase_client import db

CHOICE_EMOJIS = {
    "Rock": "🪨",
    "Paper": "📄",
    "Scissors": "✂️",
}


class RPSChoiceView(discord.ui.View):
    def __init__(self, challenger, opponent, wager):
        super().__init__(timeout=300)

        self.challenger = challenger
        self.opponent = opponent
        self.wager = wager
        self.choices = {}

    @discord.ui.button(label="🪨 Rock", style=discord.ButtonStyle.primary)
    async def rock(self, interaction, button):
        await self.make_choice(interaction, "Rock")

    @discord.ui.button(label="📄 Paper", style=discord.ButtonStyle.primary)
    async def paper(self, interaction, button):
        await self.make_choice(interaction, "Paper")

    @discord.ui.button(label="✂️ Scissors", style=discord.ButtonStyle.primary)
    async def scissor(self, interaction, button):
        await self.make_choice(interaction, "Scissors")

    async def make_choice(self, interaction, choice):

        if interaction.user not in (self.challenger, self.opponent):
            await interaction.response.send_message(
                "You are not part of this game.",
                ephemeral=True,
            )
            return
        if interaction.user.id in self.choices:
            await interaction.response.send_message(
                "You have already made your choice.",
                ephemeral=True,
            )
            return
        self.choices[interaction.user.id] = choice

        await interaction.response.send_message(
            f"You chose **{choice}**.",
            ephemeral=True,
        )

        if len(self.choices) == 2:
            await self.finish_game(interaction)

    async def finish_game(self, interaction):

        c1 = self.choices[self.challenger.id]
        c2 = self.choices[self.opponent.id]

        result = await rock_paper_scissor(c1, c2)

        if result == "Draw":
            winner_text = "It's a draw!"
        else:
            if result == c1:
                winner = self.challenger
                loser = self.opponent
            else:
                winner = self.opponent
                loser = self.challenger

            winner_text = f"🏆 {winner.mention} wins!"

            winner_ref = db.collection("users").document(str(winner.id))
            loser_ref = db.collection("users").document(str(loser.id))

            winner_ref.set(
                {
                    "coins": firestore.Increment(self.wager),
                    "transactions": firestore.ArrayUnion(
                        [
                            f"+ Won ${self.wager} from janken against {loser.display_name}"
                        ]
                    ),
                },
                merge=True,
            )
            loser_ref.set(
                {
                    "coins": firestore.Increment(-self.wager),
                    "transactions": firestore.ArrayUnion(
                        [
                            f"- Lost ${self.wager} from janken against {winner.display_name}"
                        ]
                    ),
                },
                merge=True,
            )

        embed = discord.Embed(
            title="<:gon:1480922691950088293> Rock Paper Scissors Result",
            color=discord.Color.green(),
        )

        embed.add_field(
            name=self.challenger.display_name,
            value=f"{CHOICE_EMOJIS[c1]} {c1}",
        )

        embed.add_field(
            name=self.opponent.display_name,
            value=f"{CHOICE_EMOJIS[c2]} {c2}",
        )

        embed.add_field(
            name="Outcome",
            value=winner_text,
            inline=False,
        )

        embed.set_thumbnail(
            url="https://i1.sndcdn.com/artworks-270NfGy2wimgfdqZ-wRTLdg-t1080x1080.jpg"
        )

        await interaction.message.edit(
            embed=embed,
            view=None,
        )
