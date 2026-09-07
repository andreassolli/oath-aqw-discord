import discord

from extra_commands.officer_application.utils import handle_application_submission


class OfficerApplicationModal(discord.ui.Modal, title="Officer Application"):
    q1 = discord.ui.Label(
        text="Select your area(s) of expertise",
        component=discord.ui.CheckboxGroup(
            options=[
                discord.CheckboxGroupOption(
                    label="🎫 Ticket help and monitoring",
                    value="Tickets"
                ),
                discord.CheckboxGroupOption(
                    label="🤝🏻 Recruiting new guild members",
                    value="Recruiter"
                ),
                discord.CheckboxGroupOption(
                    label="💻 Programming, art, other forms.",
                    value="Contributor"
                ),
                discord.CheckboxGroupOption(
                    label="🛡️Discord moderation",
                    value="Discord Mod"
                ),
                discord.CheckboxGroupOption(
                    label="📝 Organizing and events",
                    value="Events & Organizing"
                )
            ],
            required=True,
        ),
    )

    q2 = discord.ui.TextInput(
        label="Why do you want to be officer?",
        placeholder="Try to be concise, while still explaining how you want to contribute. You may be contacted for further info.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True,
    )
    q3 = discord.ui.TextInput(
        label="Any previous experience?",
        placeholder="No previous experience is fine, but if you have write it here.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True,
    )
    async def on_submit(self, interaction: discord.Interaction):
        questions = [
            f"{self.q1.text}",
            f"{self.q2.label}\n{self.q2.placeholder}",
            f"{self.q3.label}\n{self.q3.placeholder}",
        ]

        answers = [
            self.q1.component.values,
            self.q2.value,
            self.q3.value,
        ]

        await handle_application_submission(
            interaction,
            questions,
            answers,
        )
