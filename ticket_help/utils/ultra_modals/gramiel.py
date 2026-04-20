import discord

from ticket_help.utils.cert_utils import handle_application_submission


class GramielModal(discord.ui.Modal, title="Ultra Gramiel Application"):
    q1 = discord.ui.TextInput(
        label="Q1: Taunting Pattern",
        placeholder="How and when to taunt against Ultra Gramiel, and how long should you wait after Phase 1 to taunt?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q2 = discord.ui.TextInput(
        label="Q2: Haste Debuff, Phase 1",
        placeholder="How do you end up with haste debuff during the 1st phase?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q3 = discord.ui.TextInput(
        label="Q3: Legion Revenant Enhancements & Avoid",
        placeholder="What enhancements do you need to have for Legion Revenant, and what do you have to avoid doing?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q4 = discord.ui.TextInput(
        label="Q4: Taunting Pattern, Phase 2",
        placeholder="How do you loop the taunts in second phase, and ideally what order should each class taunt?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q5 = discord.ui.TextInput(
        label="Q5: Death's Door & Liberator Servants",
        placeholder="If the text about 'Death's Door' appears before 'Liberator' text, what should you do?",
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
            "gramiel",
            questions,
            answers,
        )
