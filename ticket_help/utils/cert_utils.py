import discord

from config import TICKET_INSPECTOR_ROLE_ID, TICKET_INSPECTORS_CHANNEL_ID
from firebase_client import db


async def handle_application_submission(interaction, app_type, questions, answers):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    channel = guild.get_channel(TICKET_INSPECTORS_CHANNEL_ID)

    if not channel:
        return await interaction.followup.send("❌ Channel not found.", ephemeral=True)

    try:
        thread = await channel.create_thread(
            name=f"📩 {app_type.title()} Application - {interaction.user.display_name}",
            type=discord.ChannelType.public_thread,
        )

        await thread.send(
            f"📩 **{app_type.title()} Application from {interaction.user.mention}**"
        )

        for q, ans in zip(questions, answers):
            await thread.send(f"**{q}**\n{ans}")

        role = guild.get_role(TICKET_INSPECTOR_ROLE_ID)
        if role:
            await channel.send(f"📮 {role.mention}, new {app_type} application!")

    except Exception as e:
        return await interaction.followup.send(f"❌ Failed: {e}", ephemeral=True)

    field = f"last_{app_type}_application_at"
    doc = db.collection("users").document(str(interaction.user.id)).get()
    data = doc.to_dict() or {}

    application_statuses = data.get("application_statuses", {})
    application_statuses[app_type] = "Under review"

    db.collection("users").document(str(interaction.user.id)).set(
        {
            field: discord.utils.utcnow(),
            "application_statuses": application_statuses,
        },
        merge=True,
    )

    await interaction.followup.send("✅ Application submitted!", ephemeral=True)
