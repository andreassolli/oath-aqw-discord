import discord

from ticket_help.utils.cert_utils import handle_application_submission


class DarkonModal(discord.ui.Modal, title="Ultra Darkon Application"):
    q1 = discord.ui.TextInput(
        label="Q1: When should LoO stop and start using 5?",
        placeholder="",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q2 = discord.ui.TextInput(
        label="Q2: What is the way to taunt at Darkon?",
        placeholder="",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q3 = discord.ui.TextInput(
        label="Q3: What does taunting the elegy do in the 3 diff phases?",
        placeholder="Elegy = Mouth Animation",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q4 = discord.ui.TextInput(
        label="Q4: What is different in P3 from P1 & P2",
        placeholder="P1, P2, P3 = Phase 1, Phase 2, Phase 3",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q5 = discord.ui.TextInput(
        label="Q5: Give some examples for DPS and healing",
        placeholder="Atleast 2 classes per type, with 1 being Free to Play.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        questions = [
            f"{self.q1.label}\n{self.q1.placeholder}",
            f"{self.q2.label}\n{self.q2.placeholder}",
            f"{self.q3.label}\n{self.q3.placeholder}",
            f"{self.q4.label}\n{self.q4.placeholder}",
            f"{self.q5.label}\n{self.q5.placeholder}",
        ]

        answers = [
            self.q1.value,
            self.q2.value,
            self.q3.value,
            self.q4.value,
            self.q5.value,
        ]

        await handle_application_submission(
            interaction,
            "darkon",
            questions,
            answers,
        )
