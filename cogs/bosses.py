import discord
from discord import app_commands
from discord.ext import commands


class Bosses(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    speaker = app_commands.Group(
        name="speaker", description="Get information for Ultra Speaker"
    )

    @speaker.command(name="guide", description="Link to the Ultra Speaker guide")
    async def ultraspeaker(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "https://discord.com/channels/1455651278590972019/1469342145017024563"
        )

    @speaker.command(name="3man", description="View the chart for 3 man taunt")
    async def three_man(self, interaction: discord.Interaction):
        embed = discord.Embed(title="3 Man Taunt Chart", color=discord.Color.blue())
        embed.set_image(
            url="https://media.discordapp.net/attachments/1469342145017024563/1490078341523308724/lr-ao-loo.png"
        )

        await interaction.response.send_message(embed=embed)

    @speaker.command(name="lem", description="View the Lem's chart for 2 man taunt")
    async def lem(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Lem's 2 Man Taunt Chart", color=discord.Color.blue()
        )
        file = discord.File("assets/lemspeaker.png", filename="lemspeaker.png")
        embed.set_image(url="attachment://lemspeaker.png")
        await interaction.response.send_message(embed=embed, file=file)

    @speaker.command(name="ap", description="View the Lem's chart for 2 man taunt")
    async def ap(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Simple AP chart for 3 man", color=discord.Color.blue()
        )
        file = discord.File("assets/apspeaker.png", filename="apspeaker.png")
        embed.set_image(url="attachment://apspeaker.png")
        await interaction.response.send_message(embed=embed, file=file)

    @speaker.command(name="loo", description="View the Lem's chart for 2 man taunt")
    async def loo(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Simple LOO chart for 3 man", color=discord.Color.blue()
        )
        file = discord.File("assets/loospeaker.png", filename="loospeaker.png")
        embed.set_image(url="attachment://loospeaker.png")
        await interaction.response.send_message(embed=embed, file=file)


async def setup(bot: commands.Bot):
    await bot.add_cog(Bosses(bot))
