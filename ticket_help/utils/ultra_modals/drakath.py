import discord

from ticket_help.utils.cert_utils import handle_application_submission


class DrakathModal(discord.ui.Modal, title="Ultra Drakath Application"):
    q1 = discord.ui.TextInput(
        label="Q1: What's the taunt thresholds?",
        placeholder="Explain why.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q2 = discord.ui.TextInput(
        label="Q2: Why/when do we have 2 taunters?",
        placeholder="How does it work?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q3 = discord.ui.TextInput(
        label="Q3: Can LR survive taunts with LoO?",
        placeholder="Assume enhancements: Arcana's Concerto, Wizard, Wizard, Penitence",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q4 = discord.ui.TextInput(
        label="Q4: Nukes, how much dmg, and type?",
        placeholder="How much damage do nukes do, and what type of damage do they do?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q5 = discord.ui.TextInput(
        label="Q5: Max def/dmg resist vs. dmg reduction?*",
        placeholder="*What would you prefer in general when fighting Drakath. Either Max defense/damage resistance, or more damage reduction, explain.",
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
