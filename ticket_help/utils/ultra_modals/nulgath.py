import discord

from ticket_help.utils.cert_utils import handle_application_submission


class NulgathModal(discord.ui.Modal, title="Ultra Nulgath Application"):
    q1 = discord.ui.TextInput(
        label="Q1: Who and when do you taunt?",
        placeholder="Which target and timing.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q2 = discord.ui.TextInput(
        label="Q2: Why and when do you die, with taunts?",
        placeholder="Assume taunting is correct, and give exact time and reason.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q3 = discord.ui.TextInput(
        label="Q3: Should you kill Blade on respawn?",
        placeholder="Why, or why not?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q4 = discord.ui.TextInput(
        label="Q4: Give 2 example comps for Nulgath",
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
        ]

        answers = [
            self.q1.value,
            self.q2.value,
            self.q3.value,
            self.q4.value,
        ]

        await handle_application_submission(
            interaction,
            "nulgath",
            questions,
            answers,
        )
