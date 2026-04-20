import discord

from ticket_help.utils.cert_utils import handle_application_submission


class DageModal(discord.ui.Modal, title="Ultra Dage Application"):
    q1 = discord.ui.TextInput(
        label="Q1: What is Flux Taunting, how do you do it?",
        placeholder="",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q2 = discord.ui.TextInput(
        label="Q2: Why do we Taunt or use Shadowblade?",
        placeholder="",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q3 = discord.ui.TextInput(
        label="Q3: When does Dage heal a massive amount?",
        placeholder="Exact time.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q4 = discord.ui.TextInput(
        label="Q4: What is most important when fighting Dage?",
        placeholder="",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q5 = discord.ui.TextInput(
        label="Q5: Give atleast 2 comps that can defeat Ultra Dage",
        placeholder="",
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
