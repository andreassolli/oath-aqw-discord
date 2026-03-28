import math
import random
from typing import Literal

import discord
from discord import app_commands, user
from discord.ext import commands
from google.cloud import firestore

from config import (
    BETA_TESTER_ROLE_ID,
    BOT_GUY_ROLE_ID,
    DISCORD_MANAGER_ROLE_ID,
    MODERATOR_ROLE_ID,
)
from economy.confirm_rocks import RockConfirmView
from economy.gamba.doom_view import DoomSpinView
from economy.gamba.utils import format_time, has_spun_today
from economy.generate_rocks import generate_rocks
from economy.helpers import paginate_items
from economy.inventory import generate_inventory
from economy.operations import buy_item, get_shop, list_item, unlist_item
from economy.rock_breaking import get_break_cooldown
from economy.rocks_view import RockView
from economy.shop import shop_embed
from economy.shop_generation import generate_shop
from economy.shop_view import ShopView
from economy.utils import rich_coins
from firebase_client import db
from inventory.utils import equip_item, get_inventory, unequip_item
from inventory.view import InventoryView


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="list-item", description="List an item for sale in the shop."
    )
    @app_commands.checks.has_any_role(
        BOT_GUY_ROLE_ID, MODERATOR_ROLE_ID, DISCORD_MANAGER_ROLE_ID
    )
    async def list_item(
        self,
        interaction: discord.Interaction,
        name: str,
        price: int,
        image: str,
        type: str,
        currency: Literal["coins", "gems"] = "coins",
        quantity: int | None = None,
    ):
        await list_item(name, price, image, currency, type, quantity)
        return await interaction.response.send_message(
            f"Listed {name} for sale in the shop.", ephemeral=True
        )

    @app_commands.command(
        name="unlist_item", description="Remove an item from the shop."
    )
    @app_commands.checks.has_any_role(
        BOT_GUY_ROLE_ID, MODERATOR_ROLE_ID, DISCORD_MANAGER_ROLE_ID
    )
    async def unlist_item(
        self,
        interaction: discord.Interaction,
        name: str,
    ):
        await unlist_item(name)
        return await interaction.response.send_message(
            f"Removed {name} from the shop.", ephemeral=True
        )

    @app_commands.command(name="buy", description="Buy an item from the shop.")
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def buy_item(self, interaction: discord.Interaction, item: str):
        user = interaction.user.id
        response = await buy_item(item, user)
        return await interaction.response.send_message(response, ephemeral=True)

    @app_commands.command(name="shop", description="List all the items in the shop.")
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def see_shop(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        items = await get_shop()
        owned_items = await get_inventory(str(interaction.user.id))
        owned_ids = {item.get("id") for item in owned_items}

        filtered = [item for item in items if item.get("id") not in owned_ids]

        total_pages = max(1, math.ceil(len(filtered) / 8))
        page_items = paginate_items(filtered, 0, 8)

        image = await generate_shop(
            items=page_items,
            userId=str(interaction.user.id),
            page=0,
            total_pages=total_pages,
        )

        file = discord.File(image, filename="shop.png")

        view = ShopView(interaction.user.id, items)

        await interaction.followup.send(
            file=file,
            view=view,
            ephemeral=True,
        )

    @app_commands.command(
        name="purse-adjust", description="Increase or decrease coins in someones purse."
    )
    @app_commands.checks.has_any_role(
        BOT_GUY_ROLE_ID, MODERATOR_ROLE_ID, DISCORD_MANAGER_ROLE_ID
    )
    async def adjust_coins(
        self, interaction: discord.Interaction, user: discord.Member, coins: int
    ):
        user_ref = db.collection("users").document(str(user.id))

        user_ref.set({"coins": firestore.Increment(coins)}, merge=True)
        return await interaction.response.send_message(
            f"{user.display_name}'s points adjusted by {coins}", ephemeral=True
        )

    @app_commands.command(
        name="purse", description="Check how many coins you have in your coin purse."
    )
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def purse(
        self, interaction: discord.Interaction, user: discord.Member | None = None
    ):
        if user:
            user_id = user.id
            user_doc = db.collection("users").document(str(user_id)).get()

            if not user_doc:
                return await interaction.response.send_message("User not found.")

            user_data = user_doc.to_dict()
            coins = user_data.get("coins", 0)
            gems = user_data.get("gems", 0)

            return await interaction.response.send_message(
                f"{user.display_name} has <:oathcoin:1462999179998531614>{coins} and <:gems:1485660490376937502>{gems}."
            )
        else:
            user_id = interaction.user.id
            user_doc = db.collection("users").document(str(user_id)).get()

            if not user_doc:
                return await interaction.response.send_message("User not found.")

            user_data = user_doc.to_dict()
            coins = user_data.get("coins", 0)
            gems = user_data.get("gems", 0)

            return await interaction.response.send_message(
                f"You ({interaction.user.display_name}) have <:oathcoin:1462999179998531614>{coins} and <:gems:1485660490376937502>{gems}."
            )

    @app_commands.command(name="doom", description="Spin the Wheel of Doom")
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def doom(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)
        has_spun, cooldown = await has_spun_today(interaction.user.id)

        if has_spun:
            return await interaction.followup.send(
                f"⏳ You already spun today. Try again in {format_time(cooldown)}",
                ephemeral=True,
            )
        spins_available = 0 if has_spun else 1
        embed = discord.Embed(
            title="🎡 Wheel of Doom",
            description=f"You have `{spins_available}` spin available, click the button below to spin!",
            color=discord.Color.red(),
        )
        embed.set_image(
            url="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/main/assets/doom.png"
        )

        view = DoomSpinView(user=interaction.user, spins_available=spins_available)

        await interaction.followup.send(
            embed=embed,
            view=view,
            ephemeral=True,
        )

    @app_commands.command(
        name="coin-leaderboard",
        description="Scout the 15 richest people in the discord.",
    )
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def coin_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild = interaction.guild
        if not guild:
            return
        embed = rich_coins(guild)
        return await interaction.followup.send(embed=embed)

    @app_commands.command(name="donate", description="Donate coins to a friend.")
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def donate(
        self, interaction: discord.Interaction, user: discord.Member, coins: int
    ):
        if coins <= 0:
            return await interaction.response.send_message(
                "Select a number higher than 0."
            )
        user_coins = (
            db.collection("users")
            .document(str(interaction.user.id))
            .get()
            .to_dict()
            .get("coins", 0)
        )
        if user_coins < coins:
            return await interaction.response.send_message(
                "You cannot donate more coins you have."
            )
        db.collection("users").document(str(interaction.user.id)).update(
            {"coins": firestore.Increment(-coins)}
        )
        db.collection("users").document(str(user.id)).update(
            {"coins": firestore.Increment(coins)}
        )

        return await interaction.response.send_message(
            f"{interaction.user.display_name} donated <:oathcoin:1462999179998531614>{coins} to {user.display_name}"
        )

    @app_commands.command(
        name="inventory", description="View the items in your inventory."
    )
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_doc = db.collection("users").document(str(interaction.user.id)).get()

        if not user_doc.exists:
            return await interaction.followup.send(
                "You don't own any items yet.", ephemeral=True
            )

        data = user_doc.to_dict() or {}
        inventory = data.get("inventory", [])

        if not inventory:
            return await interaction.followup.send(
                "Your inventory is empty.", ephemeral=True
            )

        total_pages = max(1, math.ceil(len(inventory) / 8))
        page_items = paginate_items(inventory, 0, 8)

        image = await generate_inventory(
            total_items=len(inventory),
            items=page_items,
            userId=str(interaction.user.id),
            page=0,
            total_pages=total_pages,
        )
        file = discord.File(image, filename="inventory.png")

        borders = []
        backgrounds = []
        borders.append("None")
        backgrounds.append("None")

        for item in inventory:
            item_id = item.get("id")
            item_type = item.get("type")

            if item_type == "border":
                borders.append(item_id)

            if item_type == "card":
                backgrounds.append(item_id)

        view = InventoryView(
            user_id=interaction.user.id,
            items=inventory,
            interaction=interaction,
        )

        await interaction.followup.send(
            file=file,
            view=view,
            ephemeral=True,
        )

    @app_commands.command(
        name="equip", description="Equip an item from your inventory."
    )
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def equip(self, interaction: discord.Interaction, item: str):

        response = await equip_item(str(interaction.user.id), item)

        await interaction.response.send_message(response, ephemeral=True)

    @app_commands.command(
        name="unequip", description="Unequip an item from your inventory."
    )
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def unequip(self, interaction: discord.Interaction, item: str):

        response = await unequip_item(str(interaction.user.id), item)

        await interaction.response.send_message(response, ephemeral=True)

    @app_commands.command(
        name="break-rocks", description="Break rocks for a chance to win Chaos Shards."
    )
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def view_rocks(self, interaction: discord.Interaction):
        cooldown = await get_break_cooldown(interaction.user.id)

        if cooldown is not None:
            return await interaction.response.send_message(
                f"⏳ You can break rocks again in {format_time(cooldown)}",
                ephemeral=True,
            )

        price = random.randint(600, 800)

        view = RockConfirmView(interaction.user, price)

        await interaction.response.send_message(
            f"Spend <:oathcoin:1462999179998531614>{price} to break rocks?",
            view=view,
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
