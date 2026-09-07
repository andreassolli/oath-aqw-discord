import discord

from config import OFFICER_UPDATES

async def handle_application_submission(interaction, questions, answers):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    channel = guild.get_channel(OFFICER_UPDATES)

    if not channel:
        return await interaction.followup.send("❌ Channel not found.", ephemeral=True)

    try:
        thread = await channel.create_thread(
            name=f"📩 Officer Application - {interaction.user.display_name}",
            type=discord.ChannelType.public_thread,
        )

        await thread.send(
            f"📩 **Officer Application from {interaction.user.mention}**"
        )

        for q, ans in zip(questions, answers):
            await thread.send(f"**{q}**\n{ans}")

    except Exception as e:
        return await interaction.followup.send(f"❌ Failed: {e}", ephemeral=True)

    await interaction.followup.send("✅ You application has been submitted!\nMake sure you have your DMs open. You may be contacted for further information.", ephemeral=True)
