import discord
from discord import app_commands
from discord.ext import commands
from image_generation import generate_profile_card


@app_commands.command(name="profile", description="Show your profile card")
async def profile(interaction: discord.Interaction, user: discord.Member | None = None):
    await interaction.response.defer(thinking=True)

    target = user or interaction.user
    interaction.user = target

    image_buffer = await generate_profile_card(interaction)

    await interaction.followup.send(
        file=discord.File(image_buffer, filename="profile.png")
    )
