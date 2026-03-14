import random

import discord
from google.cloud import firestore

from firebase_client import db


class BegView(discord.ui.View):
    def __init__(self, beggar: discord.Member):
        super().__init__(timeout=10)
        self.beggar = beggar
        self.donors: set[int] = set()
        self.total = 0
        self.message: discord.Message | None = None

    @discord.ui.button(
        label="Donate 1 coin",
        style=discord.ButtonStyle.primary,
    )
    async def donate(self, interaction: discord.Interaction, button):

        if self.is_finished():
            return await interaction.response.send_message(
                "Begging has ended.", ephemeral=True
            )

        donor_id = interaction.user.id

        if donor_id == self.beggar.id:
            return await interaction.response.send_message(
                "You can't donate to yourself.", ephemeral=True
            )

        if donor_id in self.donors:
            return await interaction.response.send_message(
                "You already donated.", ephemeral=True
            )

        user_ref = db.collection("users").document(str(donor_id))
        user_doc = user_ref.get()

        coins = (user_doc.to_dict() or {}).get("coins", 0)

        if coins < 1:
            return await interaction.response.send_message(
                "You don't have enough coins.", ephemeral=True
            )

        user_ref.update({"coins": firestore.Increment(-1)})

        self.donors.add(donor_id)
        self.total += 1

        await interaction.response.send_message(
            f"You donated <:oathcoin:1462999179998531614>1 to {self.beggar.display_name}.",
            ephemeral=True,
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message:
            await self.message.edit(view=self)

        self.total += random.randint(1, 6)

        beggar_ref = db.collection("users").document(str(self.beggar.id))
        beggar_ref.update({"coins": firestore.Increment(self.total)})

        if self.message:
            await self.message.channel.send(
                f"🙏 {self.beggar.mention} received "
                f"<:oathcoin:1462999179998531614>{self.total} from generous donors!"
            )
