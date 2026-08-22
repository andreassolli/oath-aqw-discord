import discord

from config import PROXY_CHANNEL
from firebase_client import db

SOCIALS_EMOJI = {
    "YouTube": "📺",
    "Twitch": "📹",
    "Twitter/X": "🐦",
    "TikTok": "📱",
}

SOCIALS = {
    "YouTube": (
        "YouTube",
        discord.PartialEmoji(name="youtube", id=1540716772615917658),
        "<:youtube:1540716772615917658>"
    ),
    "Twitch": (
        "Twitch",
        discord.PartialEmoji(name="twitch", id=1540716768945766550),
        "<:twitch:1540716768945766550>"
    ),
    "Twitter/X": (
        "Twitter",
        discord.PartialEmoji(name="twitter", id=1540716770644590693),
        "<:twitter:1540716770644590693>"
    ),
    "TikTok": (
        "TikTok",
        discord.PartialEmoji(name="tiktok", id=1540716774226395197),
        "<:tiktok:1540716774226395197>"
    ),
}


class SocialsModal(discord.ui.Modal, title="Content Creator Application"):
    def __init__(self):
        super().__init__()

        self.social_inputs = {}

        for social, data in SOCIALS.items():
            name, emoji, emoji_text = data

            item = discord.ui.TextInput(
                label=f"{SOCIALS_EMOJI[social]} {name}",
                placeholder="Username or link",
                required=False,
                max_length=100,
            )

            self.social_inputs[social] = item
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user_id = str(interaction.user.id)

        socials = {}

        for social, item in self.social_inputs.items():
            value = item.value.strip()

            if value:
                socials[social] = value

        # Save socials to Firestore
        db.collection("users").document(user_id).set(
            {
                "socials": socials,
            },
            merge=True,
        )

        guild = interaction.guild

        if guild is None:
            return await interaction.followup.send(
                "Couldn't find guild, contact Proxy.",
                ephemeral=True,
            )

        log_channel = guild.get_channel(PROXY_CHANNEL)

        if log_channel is None:
            return await interaction.followup.send(
                "Couldn't find the application log channel, contact Proxy.",
                ephemeral=True,
            )

        if not socials:
            return await interaction.followup.send(
                "Enter data.",
                ephemeral=True,
            )

        view = SocialsLog(socials, interaction.user)
        await log_channel.send(view=view)

        return await interaction.followup.send(
            "Your application has been saved.",
            ephemeral=True,
        )

class SocialsLog(discord.ui.LayoutView):
    def __init__(self, socials, user):
        super().__init__(timeout=None)

        lines = []

        for social, value in socials.items():
            info = SOCIALS[social]

            # info[2] = custom Discord emoji string
            lines.append(f"{info[2]} {value}")

        social_media = "\n".join(lines)

        self.container1 = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"**Content Creator Application** from {user.mention}"
            ),
            discord.ui.Separator(),
            discord.ui.TextDisplay(
                content=social_media
            ),
        )

        self.add_item(self.container1)
