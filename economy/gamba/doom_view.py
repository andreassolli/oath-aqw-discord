import discord


class DoomSpinView(discord.ui.View):
    def __init__(self, user: discord.Member):
        super().__init__(timeout=60)
        self.user = user

    @discord.ui.button(label="🎡 Spin the Wheel", style=discord.ButtonStyle.danger)
    async def spin(self, interaction: discord.Interaction, button):

        if interaction.user != self.user:
            await interaction.response.send_message(
                "You can't spin someone else's wheel.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        gif = discord.File("assets/wheel_spin.gif", filename="wheel_spin.gif")

        embed = discord.Embed(
            title="Wheel of Doom",
            description="Spinning...",
            color=discord.Color.red(),
        )

        embed.set_image(url="attachment://wheel_spin.gif")

        button.disabled = True

        await interaction.edit_original_response(
            embed=embed,
            attachments=[gif],
            view=self,
        )
