import random

import discord
from google.cloud.firestore import Increment

from firebase_client import db


class RockView(discord.ui.View):
    def __init__(self, user: discord.Member, rocks: list[int]):
        super().__init__(timeout=120)
        self.user = user
        self.rocks = rocks

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.user.id

    async def handle_choice(self, interaction: discord.Interaction, index: int):
        rock_type = self.rocks[index]
        user_ref = db.collection("users").document(str(self.user.id))

        if rock_type == 10:
            result = "You broke the rock, and found...\n💨 Just dust..."

        elif rock_type <= 6:
            shards = random.randint(1, 3)

            user_ref.update({"gems": Increment(shards)})

            result = (
                f"You broke the rock, and found...\n<:gems:1485660490376937502>{shards}"
            )

        elif rock_type == 7:
            shards = random.randint(1, 3)
            coins = random.randint(10, 50)

            user_ref.update({"gems": Increment(shards), "coins": Increment(coins)})

            result = (
                f"You broke the rock, and found...\n"
                f"<:gems:1485660490376937502>{shards} "
                f"and <:oathcoin:1462999179998531614>{coins}"
            )

        else:
            shards = random.randint(3, 5)

            user_ref.update({"gems": Increment(shards)})

            result = (
                f"You broke the rock, and found...\n<:gems:1485660490376937502>{shards}"
            )

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(content=result, view=self)

    @discord.ui.button(label="Left", style=discord.ButtonStyle.primary)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, 0)

    @discord.ui.button(label="Middle", style=discord.ButtonStyle.primary)
    async def middle(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, 1)

    @discord.ui.button(label="Right", style=discord.ButtonStyle.primary)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, 2)
