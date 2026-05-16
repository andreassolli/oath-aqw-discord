import discord


class CancelModal(discord.ui.Modal, title="Cancel ticket"):
    reason = discord.ui.TextDisplay(
        content="Do you wish to cancel this ticket? This action cannot be undone."
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Cancelled", ephemeral=True)
