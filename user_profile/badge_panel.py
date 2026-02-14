from pathlib import Path

import discord

from config import BADGE_CHANNEL_ID, VERIFICATION_CHANNEL_ID

from .badges_multiselect_view import BadgesMultiSelectView

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


async def setup_verification_panel(client: discord.Client):
    print("Running badge panel setup...")

    channel = client.get_channel(BADGE_CHANNEL_ID)

    if channel is None:
        channel = await client.fetch_channel(BADGE_CHANNEL_ID)

    if not isinstance(channel, discord.TextChannel):
        print("❌ Badges channel not found or not a text channel.")
        return

    async for msg in channel.history(limit=3):
        if msg.author == client.user:
            await msg.delete()

    embed = discord.Embed(
        title="Freshen up your profile card with some neat badges! ✨",
        description=(
            "🎖️ Select the badges you want to apply for below:\n\n"
            "🧳 Keep the necessary items in your inventory when applying.\n"
            "📑 You can select multiple badges per application.\n"
            "📖 Read more about <#1471212539168686345>.\n\n"
            f"🪪 *In order to apply, you must be verified in <#{VERIFICATION_CHANNEL_ID}>!*"
        ),
        color=discord.Color.blurple(),
    )
    embed.set_image(
        url="https://aq3d.com/media/r2wpnzih/dage-the-evil-art-work-aqw.jpeg"
    )
    await channel.send(embed=embed, view=BadgesMultiSelectView())
