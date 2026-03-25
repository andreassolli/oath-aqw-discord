import discord

from config import TICKET_INSPECTORS_CHANNEL_ID

# Temporary storage
user_responses = {}

QUESTIONS_STEP1 = [
    "What essential classes do you want for killing Speaker, and why would you do a 3 man over 4 man taunt?",
    "Why do we have to rotate who takes the zone, and why can there only be one at a time?",
    "How do you maximize ArchPaladins Seal and Broken Seal debuff, and what is the issue if Speaker regenerates the Health?",
    "What do you have to avoid when taunting as Lord of Order, and how do you avoid it?",
    "Why do you have to save skill 5 as Lord of Order, and how do you avoid running out of mana?",
]

QUESTIONS_STEP2 = [
    "How and when do we taunt when fighting Ultra Gramiel, and how long should you wait after Phase 1 to taunt?",
    "How do you end up with haste debuff during the 1st phase?",
    "What enhancements do you need to have for Legion Revenant, and what do you have to avoid doing?",
    "How do you loop the taunts in second phase, and ideally what order should each class taunt?",
    "If the text about 'Death's Door' appears before 'All servants of the 'Liberator' must die!', what should you do?",
]


# ---------------- MODAL 1 ---------------- #
class FirstModal(discord.ui.Modal, title="Part 1 - Ultra Speaker"):
    q1 = discord.ui.TextInput(
        label="Classes & Taunt Strategy",
        placeholder="What essential classes do you want for Speaker, and why do a 3 man over 4 man taunt?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q2 = discord.ui.TextInput(
        label="Zone Rotation",
        placeholder="Why do we have to rotate who takes the zone, and why can there only be one at a time?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q3 = discord.ui.TextInput(
        label="Maximize APs debuffs, and Regeneration",
        placeholder="How do you maximize APs Seal & Broken Seal debuff, and what's the issue if Speaker regenerates?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q4 = discord.ui.TextInput(
        label="Taunting as Lord of Order",
        placeholder="What do you have to avoid when taunting as Lord of Order, and how do you avoid it?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q5 = discord.ui.TextInput(
        label="Mana Issues and skill 5, Lord of Order",
        placeholder="Why do you have to save skill 5 as Lord of Order, and how do you avoid mana issues?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_responses[interaction.user.id] = {
            "step1": [
                self.q1.value,
                self.q2.value,
                self.q3.value,
                self.q4.value,
                self.q5.value,
            ]
        }

        await interaction.response.send_message(
            "Part 1 - Ultra Speaker completed. Click below for the second and final part, Ultra Gramiel.",
            view=NextStepView(),
            ephemeral=True,
        )


# ---------------- MODAL 2 ---------------- #
class SecondModal(discord.ui.Modal, title="Step 2 - Ultra Gramiel"):
    q6 = discord.ui.TextInput(
        label="Taunting Pattern",
        placeholder="How and when to taunt against Ultra Gramiel, and how long should you wait after Phase 1 to taunt?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q7 = discord.ui.TextInput(
        label="Haste Debuff, Phase 1",
        placeholder="How do you end up with haste debuff during the 1st phase?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q8 = discord.ui.TextInput(
        label="Legion Revenant Enhancements & Avoid",
        placeholder="What enhancements do you need to have for Legion Revenant, and what do you have to avoid doing?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q9 = discord.ui.TextInput(
        label="Taunting Pattern, Phase 2",
        placeholder="How do you loop the taunts in second phase, and ideally what order should each class taunt?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q10 = discord.ui.TextInput(
        label="Death's Door & Liberator Servants",
        placeholder="If the text about 'Death's Door' appears before 'Liberator' text, what should you do?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        data = user_responses.get(interaction.user.id, {})

        data["step2"] = [
            self.q6.value,
            self.q7.value,
            self.q8.value,
            self.q9.value,
            self.q10.value,
        ]
        guild = interaction.guild
        if not guild:
            return
        channel = guild.get_channel(TICKET_INSPECTORS_CHANNEL_ID)
        if not channel or not isinstance(channel, discord.TextChannel):
            return
        # Create thread
        thread = await channel.create_thread(
            name=f"Application from {interaction.user.display_name}",
            type=discord.ChannelType.public_thread,
        )

        # Format message
        content = "**Application to become an Experienced Helper**\n\n"

        # Step 1
        for q, ans in zip(QUESTIONS_STEP1, data["step1"]):
            content += f"**{q}**\n{ans}\n\n"

        # Step 2
        for q, ans in zip(QUESTIONS_STEP2, data["step2"]):
            content += f"**{q}**\n{ans}\n\n"

        await thread.send(content)

        # Cleanup
        user_responses.pop(interaction.user.id, None)

        await interaction.response.send_message(
            "✅ Submission complete! A Ticket Inspector will review your application.",
            ephemeral=True,
        )


# ---------------- BUTTON VIEWS ---------------- #
class StartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Start application",
        style=discord.ButtonStyle.primary,
        custom_id="start_application_button",  # REQUIRED
    )
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FirstModal())


class NextStepView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Part 2",
        style=discord.ButtonStyle.success,
        custom_id="application_part2_button",
    )
    async def next_step(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(SecondModal())
