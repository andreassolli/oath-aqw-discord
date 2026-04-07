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


async def setup(bot: commands.Bot):
    await bot.add_cog(Bosses(bot))
