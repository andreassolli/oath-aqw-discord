import discord

from economy.generate_rocks import generate_rocks
from economy.rock_breaking import buy_rock_break
from economy.rocks_view import RockView


class RockConfirmView(discord.ui.View):
    def __init__(self, user: discord.User, amount: int):
        super().__init__(timeout=60)
        self.user = user
        self.amount = amount

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.user.id

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        can_buy = buy_rock_break(self.user, self.amount)

        if not can_buy:
            return await interaction.response.send_message(
                "You don't have enough coins.", ephemeral=True
            )

        buffer, rocks = generate_rocks()
        file = discord.File(buffer, filename="rocks.png")

        view = RockView(self.user, rocks)

        # disable buttons
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=f"You paid <:oathcoin:1462999179998531614>{self.amount} to break rocks.",
            view=self,
        )

        await interaction.followup.send(file=file, view=view, ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(content="❌ Cancelled.", view=self)
