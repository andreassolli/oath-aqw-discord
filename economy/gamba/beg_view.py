import random

import discord
from google.cloud import firestore

from firebase_client import db


class BegView(discord.ui.View):
    def __init__(self, beggar: discord.Member):
        super().__init__(timeout=60)
        self.beggar = beggar
        self.donors: set[int] = set()
        self.donor_names: set[str] = set()
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
        self.donor_names.add(interaction.user.display_name)
        self.total += 1
        return await interaction.response.send_message(
            f"Donated <:oathcoin:1462999179998531614>1 to {self.beggar.display_name}",
            ephemeral=True,
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message:
            await self.message.edit(view=self)

        self.total += random.randint(6, 10)
        random_odds = random.randint(1, 100)

        if random_odds == 1 and len(self.donors) > 0:
            random_index = random.randint(0, len(self.donors) - 1)
            stealer_id = list(self.donors)[random_index]
            stealer_ref = db.collection("users").document(str(stealer_id))
            stealer_name = list(self.donor_names)[random_index]
            stealer_ref.update({"coins": firestore.Increment(self.total)})
            if self.message:
                await self.message.channel.send(
                    f"<:GoobShock:1463149045731299328> {stealer_name} took of with all the coins! "
                    f"A total of <:oathcoin:1462999179998531614>{self.total} was stolen."
                )

        else:
            beggar_ref = db.collection("users").document(str(self.beggar.id))
            beggar_ref.update({"coins": firestore.Increment(self.total)})
            donor_names_string = ", ".join(self.donor_names)
            if self.message:
                await self.message.channel.send(
                    f"<:GoobHeart:1459836996381048863> {self.beggar.mention} received "
                    f"<:oathcoin:1462999179998531614>{self.total} from {donor_names_string} and a mysterious donor!"
                )
