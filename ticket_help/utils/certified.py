from datetime import timedelta

import discord
from discord.ui import Select

from config import TICKET_INSPECTOR_ROLE_ID, TICKET_INSPECTORS_CHANNEL_ID
from firebase_client import db

QUESTIONS_STEP1 = [
    "Q1: Classes & Taunt Strategy\nWhat essential classes do you want for Speaker, and why do a 3 man over 4 man taunt?",
    "Q2: Zone Rotation\nWhy do we have to rotate who takes the zone, and why can there only be one at a time?",
    "Q3: Maximize APs debuffs, and Regeneration\nHow do you maximize APs Seal & Broken Seal debuff, and how do you avoid Speaker regenerating?",
    "Q4: Taunting as Lord of Order\nWhat do you have to do when taunting as LoO to avoid being stuck in the zone?",
    "Q5: Mana Issues and skill 5, Lord of Order\nWhy do you have to save skill 5 as Lord of Order, and how do you avoid mana issues?",
]

QUESTIONS_STEP2 = [
    "Q6: Taunting Pattern\nHow and when to taunt against Ultra Gramiel, and how long should you wait after Phase 1 to taunt?",
    "Q7: Haste Debuff, Phase 1\nHow do you end up with haste debuff during the 1st phase?",
    "Q8: Legion Revenant Enhancements & Avoid\nWhat enhancements do you need to have for Legion Revenant, and what do you have to avoid doing?",
    "Q9: Taunting Pattern, Phase 2\nHow do you loop the taunts in second phase, and ideally what order should each class taunt?",
    "Q10: Death's Door & Liberator Servants\nIf the text about 'Death's Door' appears before 'Liberator' text, what should you do?",
]


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
        await handle_application_submission(
            interaction,
            "speaker",
            QUESTIONS_STEP1,
            [self.q1.value, self.q2.value, self.q3.value, self.q4.value, self.q5.value],
        )


class GramielModal(discord.ui.Modal, title="Ultra Gramiel Application"):
    q6 = discord.ui.TextInput(
        label="Q6: Taunting Pattern",
        placeholder="How and when to taunt against Ultra Gramiel, and how long should you wait after Phase 1 to taunt?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q7 = discord.ui.TextInput(
        label="Q7: Haste Debuff, Phase 1",
        placeholder="How do you end up with haste debuff during the 1st phase?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q8 = discord.ui.TextInput(
        label="Q8: Legion Revenant Enhancements & Avoid",
        placeholder="What enhancements do you need to have for Legion Revenant, and what do you have to avoid doing?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q9 = discord.ui.TextInput(
        label="Q9: Taunting Pattern, Phase 2",
        placeholder="How do you loop the taunts in second phase, and ideally what order should each class taunt?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q10 = discord.ui.TextInput(
        label="Q10: Death's Door & Liberator Servants",
        placeholder="If the text about 'Death's Door' appears before 'Liberator' text, what should you do?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await handle_application_submission(
            interaction,
            "gramiel",
            QUESTIONS_STEP2,
            [
                self.q6.value,
                self.q7.value,
                self.q8.value,
                self.q9.value,
                self.q10.value,
            ],
        )


async def handle_application_submission(interaction, app_type, questions, answers):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    channel = guild.get_channel(TICKET_INSPECTORS_CHANNEL_ID)

    if not channel:
        return await interaction.followup.send("❌ Channel not found.", ephemeral=True)

    try:
        thread = await channel.create_thread(
            name=f"📩 {app_type.title()} Application - {interaction.user.display_name}",
            type=discord.ChannelType.public_thread,
        )

        await thread.send(
            f"📩 **{app_type.title()} Application from {interaction.user.mention}**"
        )

        for q, ans in zip(questions, answers):
            await thread.send(f"**{q}**\n{ans}")

        role = guild.get_role(TICKET_INSPECTOR_ROLE_ID)
        if role:
            await channel.send(f"📮 {role.mention}, new {app_type} application!")

    except Exception as e:
        return await interaction.followup.send(f"❌ Failed: {e}", ephemeral=True)

    field = f"last_{app_type}_application_at"

    db.collection("users").document(str(interaction.user.id)).set(
        {
            field: discord.utils.utcnow(),
        },
        merge=True,
    )

    await interaction.followup.send("✅ Application submitted!", ephemeral=True)


class ApplicationSelectView(discord.ui.View):
    def __init__(self, user_data):
        super().__init__(timeout=None)

        now = discord.utils.utcnow()

        def get_remaining(field):
            last = user_data.get(field)
            if not last:
                return None

            remaining = timedelta(days=3) - (now - last)
            if remaining.total_seconds() <= 0:
                return None

            return remaining

        def is_on_cooldown(field):
            last = user_data.get(field)
            if not last:
                return False
            return now - last < timedelta(days=3)

        speaker_disabled = is_on_cooldown("last_speaker_application_at")
        gramiel_disabled = is_on_cooldown("last_gramiel_application_at")

        self.select: Select = Select(
            placeholder="Choose application...",
            options=[
                discord.SelectOption(
                    label="Ultra Speaker",
                    value="speaker",
                    description="Apply for Speaker",
                    emoji="🗣️",
                ),
                discord.SelectOption(
                    label="Ultra Gramiel",
                    value="gramiel",
                    description="Apply for Gramiel",
                    emoji="🪽",
                ),
            ],
        )

        speaker_opt = self.select.options[0]
        gramiel_opt = self.select.options[1]

        if speaker_disabled:
            remaining = get_remaining("last_speaker_application_at")
            if remaining:
                speaker_opt.description = (
                    f"Cooldown ({remaining.days}d {remaining.seconds // 3600}h)"
                )
            speaker_opt.emoji = "⛔"

        if gramiel_disabled:
            remaining = get_remaining("last_gramiel_application_at")
            if remaining:
                gramiel_opt.description = (
                    f"Cooldown ({remaining.days}d {remaining.seconds // 3600}h)"
                )
            gramiel_opt.emoji = "⛔"

        self.speaker_disabled = speaker_disabled
        self.gramiel_disabled = gramiel_disabled

        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        choice = self.select.values[0]

        if (choice == "speaker" and self.speaker_disabled) or (
            choice == "gramiel" and self.gramiel_disabled
        ):
            return await interaction.response.send_message(
                "⏳ This application is still on cooldown.",
                ephemeral=True,
            )

        self.select.disabled = True
        await interaction.message.edit(view=self)

        if choice == "speaker":
            await interaction.response.send_modal(SpeakerModal())
        else:
            await interaction.response.send_modal(GramielModal())
