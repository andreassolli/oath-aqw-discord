import discord
from discord import app_commands
from discord.ext import commands


class Extra(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="elp", description="Call for ELP")
    async def elp(self, interaction: discord.Interaction):
        await interaction.response.send_message("ELP ELLPPPPP CALL DRIADGEEEEEEEEEEEE")

    @app_commands.command(name="oath", description="Call for Oath")
    async def oath(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="To the Oath we Swear", color=discord.Color.purple()
        )
        embed.set_image(url="assets/takeoath.gif")
        embed.add_field(
            name="",
            value=("I take no Throne, for there is no honor in tyranny.!"),
            inline=True,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Extra(bot))
