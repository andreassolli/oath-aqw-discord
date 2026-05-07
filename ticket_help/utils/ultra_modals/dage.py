import discord

from ticket_help.utils.cert_utils import handle_application_submission


class DageModal(discord.ui.Modal, title="Ultra Dage Application"):
    q1 = discord.ui.TextInput(
        label="Q1: How do we taunt as CAV?",
        placeholder="Explain either loop taunt or flux taunt. CAV = Chaos Avenger",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q2 = discord.ui.TextInput(
        label="Q2: Why Taunt or use Shadowblade?",
        placeholder="Shadowblade = Scroll or Classic Ninja skill 3",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q3 = discord.ui.TextInput(
        label="Q3: When is Decay needed? Exact time!",
        placeholder="",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q4 = discord.ui.TextInput(
        label="Q4: List key aspects to keep in mind.",
        placeholder="When fighting Ultra Dage. Both what to avoid, and what to do.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q5 = discord.ui.TextInput(
        label="Q5: Give 2 example comps",
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
            "dage",
            questions,
            answers,
        )
