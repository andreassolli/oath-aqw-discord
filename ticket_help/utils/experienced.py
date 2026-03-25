import discord

from config import TICKET_INSPECTORS_CHANNEL_ID

# Temporary storage
user_responses = {}


# ---------------- MODAL 1 ---------------- #
class FirstModal(discord.ui.Modal, title="Step 1 - Questions"):
    q1 = discord.ui.TextInput(label="Question 1")
    q2 = discord.ui.TextInput(label="Question 2")
    q3 = discord.ui.TextInput(label="Question 3")
    q4 = discord.ui.TextInput(label="Question 4")
    q5 = discord.ui.TextInput(label="Question 5")

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
            "Step 1 completed. Click below to continue.",
            view=NextStepView(),
            ephemeral=True,
        )


# ---------------- MODAL 2 ---------------- #
class SecondModal(discord.ui.Modal, title="Step 2 - More Questions"):
    q6 = discord.ui.TextInput(label="Question 6")
    q7 = discord.ui.TextInput(label="Question 7")
    q8 = discord.ui.TextInput(label="Question 8")
    q9 = discord.ui.TextInput(label="Question 9")
    q10 = discord.ui.TextInput(label="Question 10")

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
            name=f"Submission from {interaction.user}",
            type=discord.ChannelType.public_thread,
        )

        # Format message
        content = "**Submission Results**\n\n"

        for i, ans in enumerate(data["step1"], start=1):
            content += f"**Q{i}:** {ans}\n"

        for i, ans in enumerate(data["step2"], start=6):
            content += f"**Q{i}:** {ans}\n"

        await thread.send(content)

        # Cleanup
        user_responses.pop(interaction.user.id, None)

        await interaction.response.send_message(
            "✅ Submission complete! Thread created.", ephemeral=True
        )


# ---------------- BUTTON VIEWS ---------------- #
class StartView(discord.ui.View):
    @discord.ui.button(label="Start Form", style=discord.ButtonStyle.primary)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FirstModal())


class NextStepView(discord.ui.View):
    @discord.ui.button(label="Next", style=discord.ButtonStyle.success)
    async def next_step(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(SecondModal())
