import discord

from extra_commands.record_holder import record_holder


class LeaderboardView(discord.ui.View):
    @discord.ui.button(label="🏅Points", style=discord.ButtonStyle.primary)
    async def points(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if not guild:
            return
        embed = await record_holder("points", guild)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🎲Counting", style=discord.ButtonStyle.secondary)
    async def counts(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if not guild:
            return
        embed = await record_holder("counts", guild)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🔖Tickets", style=discord.ButtonStyle.success)
    async def claimed(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild = interaction.guild
        if not guild:
            return
        embed = await record_holder("claimed", guild)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🪙Coins", style=discord.ButtonStyle.secondary)
    async def coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if not guild:
            return
        embed = await record_holder("coins", guild)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🧩AQWordle", style=discord.ButtonStyle.success)
    async def aqwordle(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild = interaction.guild
        if not guild:
            return
        embed = await record_holder("aqwordle", guild)
        await interaction.response.edit_message(embed=embed, view=self)
