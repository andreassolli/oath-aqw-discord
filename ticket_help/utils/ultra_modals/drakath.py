import discord

from ticket_help.utils.cert_utils import handle_application_submission


class DrakathModal(discord.ui.Modal, title="Ultra Drakath Application"):
    q1 = discord.ui.TextInput(
        label="Q1: What's the Taunt thresholds?",
        placeholder="Explain why.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q2 = discord.ui.TextInput(
        label="Q2: Why/when do we have 2 taunters? How does it work?",
        placeholder="",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q3 = discord.ui.TextInput(
        label="Q3: Can LR survive taunts at 2.9K HP?",
        placeholder="Expand a bit!",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q4 = discord.ui.TextInput(
        label="Q4: Max defense, or more damage reduction?*",
        placeholder="*What would you prefer in general when fighting Drakath",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q5 = discord.ui.TextInput(
        label="Q5: How much damage, and what type, are the nukes?",
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
            "drakath",
            questions,
            answers,
        )
