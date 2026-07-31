import random

import discord
from google.cloud.firestore import Increment
from coin_helper import apply_gem_boost
from assets_caching import ROCKS_CACHE
from economy.generate_rocks import generate_rocks_from_ids
from firebase_client import db


class RockView(discord.ui.View):
    def __init__(self, user: discord.User, rocks: list[int]):
        super().__init__(timeout=120)
        self.user = user
        self.rocks = rocks

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.user.id

    async def handle_choice(self, interaction: discord.Interaction, index: int):
        rock_type = self.rocks[index]
        user_ref = db.collection("users").document(str(self.user.id))

        if rock_type == 10:
            result = "You broke the rock, and found... 💨 Just dust..."

        elif rock_type <= 6:
            shards = random.randint(1, 3)
            new_shards, boost_reasons = apply_gem_boost(shards)
            boost_text = ""

            if boost_reasons:
                boost_text = "\n" + "\n".join(
                    f"{reason} active!" for reason in boost_reasons
                )

            result = boost_text

            user_ref.update({"gems": Increment(new_shards)})

            result+=f"You broke the rock, and found... <:gems:1485660490376937502>{new_shards}"


        elif rock_type == 9:
            shards = random.randint(1, 3)
            coins = random.randint(10, 50)
            new_shards, boost_reasons = apply_gem_boost(shards)
            boost_text = ""

            if boost_reasons:
                boost_text = "\n" + "\n".join(
                    f"{reason} active!" for reason in boost_reasons
                )

            result = boost_text

            user_ref.update({"gems": Increment(new_shards), "coins": Increment(coins)})

            result+=f"You broke the rock, and found...\n<:gems:1485660490376937502>{new_shards} and <:oathcoin:1462999179998531614>{coins}"

        else:
            shards = random.randint(3, 5)
            new_shards, boost_reasons = apply_gem_boost(shards)
            boost_text = ""

            if boost_reasons:
                boost_text = "\n" + "\n".join(
                    f"{reason} active!" for reason in boost_reasons
                )

            result = boost_text
            user_ref.update({"gems": Increment(new_shards)})

            result+=f"You broke the rock, and found... <:gems:1485660490376937502>{new_shards}"

        # Replace the chosen rock with 10–15
        if rock_type == 9:
            self.rocks[index] = 16
        else:
            replacement_pool = [k for k in ROCKS_CACHE if 10 <= k <= 15]
            self.rocks[index] = random.choice(replacement_pool)

        # Generate updated image
        buffer = generate_rocks_from_ids(self.rocks)
        file = discord.File(buffer, filename="rocks.png")

        # Disable buttons (you already do this)
        for child in self.children:
            child.disabled = True

        # Edit original message WITH new image
        await interaction.response.edit_message(
            content=result, attachments=[file], view=self
        )

        # Send result message
        # await interaction.followup.send(content=result, ephemeral=True)

    @discord.ui.button(label="Left", style=discord.ButtonStyle.primary)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, 0)

    @discord.ui.button(label="Middle", style=discord.ButtonStyle.primary)
    async def middle(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, 1)

    @discord.ui.button(label="Right", style=discord.ButtonStyle.primary)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, 2)
