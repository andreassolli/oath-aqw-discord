import discord

from ticket_help.utils.cert_utils import handle_application_submission


class DragoModal(discord.ui.Modal, title="Ultra Drago Application"):
    q1 = discord.ui.TextInput(
        label="Q1: Who taunts what?",
        placeholder="Class and target.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q2 = discord.ui.TextInput(
        label="Q2: What boosted gear should you use?",
        placeholder="",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q3 = discord.ui.TextInput(
        label="Q3: Why do we need to taunt Bow/Right?",
        placeholder="",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q4 = discord.ui.TextInput(
        label="Q4: Why do we taunt Executioner/Left?",
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
            "drago",
            questions,
            answers,
        )
