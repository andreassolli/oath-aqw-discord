import discord

from config import VERIFICATION_CHANNEL_ID
from user_verification.verification_buttons import VerificationButtonView


async def setup_verification_panel(client: discord.Client):
    channel = client.get_channel(VERIFICATION_CHANNEL_ID)

    if not isinstance(channel, discord.TextChannel):
        print("❌ Verification channel not found. Check VERIFICATION_CHANNEL_ID.")
        return

    async for msg in channel.history(limit=3):
        if msg.author == client.user:
            await msg.delete()

    embed = discord.Embed(
        title="New to the server or want to join the guild?",
        description=(
            "Click one of the buttons below:\n\n"
            "✅ **Verify me** – for server verification\n"
            "🛡️ **I want to join Oath** – to apply to the guild"
        ),
        color=discord.Color.blurple(),
    )

    embed.set_image(url="https://pbs.twimg.com/media/D0BrGESWwAA1Jmv.jpg")

    await channel.send(embed=embed, view=VerificationButtonView())
