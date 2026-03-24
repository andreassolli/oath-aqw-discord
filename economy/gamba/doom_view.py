import asyncio
import random

import discord
from google.cloud import firestore

from config import ASCENDED_ROLE_ID, INITIATE_ROLE_ID, OFFICER_ROLE_ID
from economy.gamba.utils import set_spin_today
from firebase_client import db


class DoomSpinView(discord.ui.View):
    def __init__(self, user: discord.Member, spins_available: int):
        super().__init__(timeout=300)

        self.user = user
        self.spins_available = spins_available
        self.spinning = False  # local lock

        if spins_available == 0:
            for item in self.children:
                item.disabled = True

    @discord.ui.button(label="🎡 Spin the Wheel", style=discord.ButtonStyle.red)
    async def spin(self, interaction: discord.Interaction, button):

        if interaction.user != self.user:
            await interaction.response.send_message(
                "You can't spin someone else's wheel.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        if self.spinning:
            await interaction.response.send_message(
                "The wheel is already spinning!",
                ephemeral=True,
            )
            return

        self.spinning = True
        button.disabled = True
        # pick result immediately
        result = random.randint(250, 350)
        await set_spin_today(interaction.user.id)
        embed = discord.Embed(
            title="🎡 Wheel of Doom",
            description="Spinning...",
            color=discord.Color.red(),
        )

        embed.set_image(
            url="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/main/assets/wheel_spin.gif"
        )

        button.disabled = True

        await interaction.edit_original_response(
            embed=embed,
            view=self,
        )

        # wait for gif duration
        await asyncio.sleep(4)
        multiplier = 1
        bonus_text = ""
        new_result = result
        if any(role.id == ASCENDED_ROLE_ID for role in interaction.user.roles):
            multiplier = 1.1
            new_result = int(result * multiplier)
            bonus_text = f"\nThanks to your **<:ascended:1485289045524484126>Ascended** role, you got 10% bonus coins!\nTotal payout: <:oathcoin:1462999179998531614>`{new_result}`"
        elif any(role.id == OFFICER_ROLE_ID for role in interaction.user.roles):
            multiplier = 1.07
            new_result = int(result * multiplier)
            bonus_text = f"\nThanks to your **<:oath2:1457452511635046492>Officer** role, you got 7% bonus coins!\nTotal payout: <:oathcoin:1462999179998531614>`{new_result}`"
        elif any(role.id == INITIATE_ROLE_ID for role in interaction.user.roles):
            multiplier = 1.05
            new_result = int(result * multiplier)
            bonus_text = f"\nThanks to your **<:oath:1457451850184917122>Initiate** role, you got 5% bonus coins!\nTotal payout: <:oathcoin:1462999179998531614>`{new_result}`"

        result_embed = discord.Embed(
            title="🎡 Wheel of Doom",
            description=f"You won <:oathcoin:1462999179998531614>`{result}`!{bonus_text}",
            color=discord.Color.gold(),
        )
        result_embed.set_image(
            url="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/main/assets/doom.png"
        )
        user_ref = db.collection("users").document(str(interaction.user.id))

        user_ref.set(
            {"coins": firestore.Increment(new_result)},
            merge=True,
        )

        await interaction.edit_original_response(
            embed=result_embed,
            view=self,
        )
