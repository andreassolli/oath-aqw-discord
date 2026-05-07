import asyncio
import random

import discord
from google.cloud import firestore

from config import (
    ASCENDED_ROLE_ID,
    INITIATE_ROLE_ID,
    OFFICER_ROLE_ID,
    POTW_ROLE_ID,
    TRANSCENDED_ROLE_ID,
)
from economy.gamba.utils import set_spin_today
from firebase_client import db
from inventory.utils import add_item


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
        drop = random.randint(1, 20)
        drop_text = ""
        if drop == 1:
            await add_item(
                str(interaction.user.id),
                "Doom Card",
                "card",
                "doom_card.png",
                "doom_card_item.png",
                "legendary",
            )
            drop_text = "\n\nYou also won the **Secret Rare** Doom Card! It has been added to your inventory."
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
        role_bonuses = [
            (
                POTW_ROLE_ID,
                1.125,
                "Player of the Week",
                "<:potwBadge:1476938152861241565>",
                12.5,
            ),
            (
                TRANSCENDED_ROLE_ID,
                1.11,
                "Ascended",
                "<:ascended:1485289045524484126>",
                11,
            ),
            (ASCENDED_ROLE_ID, 1.1, "Ascended", "<:ascended:1485289045524484126>", 10),
            (OFFICER_ROLE_ID, 1.07, "Officer", "<:oath2:1457452511635046492>", 7),
            (INITIATE_ROLE_ID, 1.05, "Initiate", "<:oath:1457451850184917122>", 5),
        ]

        user_role_ids = {role.id for role in interaction.user.roles}

        for role_id, multiplier, name, emoji, percent in role_bonuses:
            if role_id in user_role_ids:
                new_result = int(result * multiplier)
                bonus_text = (
                    f"\nThanks to your **{emoji}{name}** role, you got {percent}% bonus coins!"
                    f"\nTotal payout: <:oathcoin:1462999179998531614>`{new_result}`"
                )
                break
        result_embed = discord.Embed(
            title="🎡 Wheel of Doom",
            description=f"You won <:oathcoin:1462999179998531614>`{result}`!{bonus_text}{drop_text}",
            color=discord.Color.gold(),
        )
        result_embed.set_image(
            url="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/main/assets/doom.png"
        )
        user_ref = db.collection("users").document(str(interaction.user.id))

        user_ref.set(
            {
                "coins": firestore.Increment(new_result),
                "transactions": firestore.ArrayUnion(
                    [f"+ Won ${new_result} from the Wheel of Doom"]
                ),
            },
            merge=True,
        )

        await interaction.edit_original_response(
            embed=result_embed,
            view=self,
        )
