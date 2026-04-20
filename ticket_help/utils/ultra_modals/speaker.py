import discord

from ticket_help.utils.cert_utils import handle_application_submission


class SpeakerModal(discord.ui.Modal, title="Ultra Speaker Application"):
    q1 = discord.ui.TextInput(
        label="Q1: Classes & Taunt Strategy",
        placeholder="What essential classes do you want for Speaker, and why do a 3 man over 4 man taunt?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q2 = discord.ui.TextInput(
        label="Q2: Zone Rotation",
        placeholder="Why do we have to rotate who takes the zone, and why can there only be one at a time?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q3 = discord.ui.TextInput(
        label="Q3: Maximize APs debuffs, and Regeneration",
        placeholder="How do you maximize APs Seal & Broken Seal debuff, and how do you avoid Speaker regenerating?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q4 = discord.ui.TextInput(
        label="Q4: Taunting as Lord of Order",
        placeholder="What do you have to do when taunting as LoO to avoid being stuck in the zone?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q5 = discord.ui.TextInput(
        label="Q5: Mana Issues and skill 5, Lord of Order",
        placeholder="Why do you have to save skill 5 as Lord of Order, and how do you avoid mana issues?",
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
            "speaker",
            questions,
            answers,
        )
