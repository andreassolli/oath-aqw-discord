from datetime import timedelta

import discord
from discord.ui import Select

from config import TICKET_INSPECTOR_ROLE_ID, TICKET_INSPECTORS_CHANNEL_ID
from firebase_client import db
from ticket_help.utils.ultra_modals.dage import DageModal
from ticket_help.utils.ultra_modals.darkon import DarkonModal
from ticket_help.utils.ultra_modals.drago import DragoModal
from ticket_help.utils.ultra_modals.drakath import DrakathModal
from ticket_help.utils.ultra_modals.gramiel import GramielModal
from ticket_help.utils.ultra_modals.nulgath import NulgathModal
from ticket_help.utils.ultra_modals.speaker import SpeakerModal

APPLICATIONS = {
    "speaker": {
        "label": "Ultra Speaker",
        "description": "Apply for Speaker",
        "emoji": "🗣️",
        "modal": SpeakerModal,
    },
    "gramiel": {
        "label": "Ultra Gramiel",
        "description": "Apply for Gramiel",
        "emoji": "🪽",
        "modal": GramielModal,
    },
    "dage": {
        "label": "Ultra Dage",
        "description": "Apply for Dage",
        "emoji": "💀",
        "modal": DageModal,
    },
    "drago": {
        "label": "Ultra Drago",
        "description": "Apply for Drago",
        "emoji": "👑",
        "modal": DragoModal,
    },
    "darkon": {
        "label": "Ultra Darkon",
        "description": "Apply for Darkon",
        "emoji": "🌑",
        "modal": DarkonModal,
    },
    "nulgath": {
        "label": "Ultra Nulgath",
        "description": "Apply for Nulgath",
        "emoji": "🧌",
        "modal": NulgathModal,
    },
    "drakath": {
        "label": "Ultra Drakath",
        "description": "Apply for Drakath",
        "emoji": "🔮",
        "modal": DrakathModal,
    },
}


class ApplicationSelectView(discord.ui.View):
    def __init__(self, user_data):
        super().__init__(timeout=None)

        now = discord.utils.utcnow()

        def get_remaining(field):
            last = user_data.get(field)
            if not last:
                return None

            remaining = timedelta(days=3) - (now - last)
            if remaining.total_seconds() <= 0:
                return None

            return remaining

        options = []
        self.cooldowns = {}

        for key, data in APPLICATIONS.items():
            field = f"last_{key}_application_at"
            last = user_data.get(field)

            disabled = last and (now - last < timedelta(days=3))
            self.cooldowns[key] = disabled

            description = data["description"]
            emoji = data["emoji"]

            if disabled:
                remaining = get_remaining(field)
                if remaining:
                    hours = remaining.seconds // 3600
                    description = f"Cooldown ({remaining.days}d {hours}h)"
                emoji = "⛔"

            options.append(
                discord.SelectOption(
                    label=data["label"],
                    value=key,
                    description=description,
                    emoji=emoji,
                )
            )

        self.select = Select(
            placeholder="Choose application...",
            options=options,
        )

        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        choice = self.select.values[0]

        if self.cooldowns.get(choice):
            return await interaction.response.send_message(
                "⏳ This application is still on cooldown.",
                ephemeral=True,
            )

        self.select.disabled = True

        modal_class = APPLICATIONS[choice]["modal"]
        await interaction.response.send_modal(modal_class())
