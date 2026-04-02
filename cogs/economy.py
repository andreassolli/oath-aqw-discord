import math
import random
from datetime import datetime, timedelta
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
        image: str,
        type: Literal["card", "border", "item"],
        coin_price: int = 0,
        shard_price: int = 0,
        quantity: int | None = None,
        priority: int | None = None,
        invisible: bool = False,
        rarity: Literal["common", "uncommon", "rare", "epic", "legendary"] = "common",
    ):
        await list_item(
            name,
            coin_price,
            shard_price,
            image,
            type,
            quantity,
            priority,
            invisible,
            rarity,
        )
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

    @app_commands.command(name="shop", description="List all the items in the shop.")
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def see_shop(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)
        has_discord_manager_role = any(
            role.id == DISCORD_MANAGER_ROLE_ID for role in interaction.user.roles
        )
        items = await get_shop()
        owned_items = await get_inventory(str(interaction.user.id))
        owned_ids = {item.get("image") for item in owned_items}
        SPECIAL_ITEM = "gold_signature_card"
        REQUIRED_ITEM = "gold_card.png"
        BETA_CARDS = [
            "beta_green_card.png",
            "beta_white_card.png",
            "beta_black_card.png",
        ]
        for item in items:
            if item.get("image") == SPECIAL_ITEM:
                if REQUIRED_ITEM in owned_ids:
                    item["coin_price"] = 500
            if item.get("image") in BETA_CARDS:
                if any(beta in owned_ids for beta in BETA_CARDS):
                    item["coin_price"] = 0

        if has_discord_manager_role:
            filtered = [item for item in items if item.get("image") not in owned_ids]
        else:
            filtered = [
                item
                for item in items
                if item.get("image") not in owned_ids
                and not item.get("invisible", False)
            ]
        sorted_filtered = sorted(
            filtered, key=lambda x: x.get("priority", 0), reverse=True
        )

        total_pages = max(1, math.ceil(len(sorted_filtered) / 8))
        page_items = paginate_items(sorted_filtered, 0, 8)

        image = await generate_shop(
            items=page_items,
            userId=str(interaction.user.id),
            page=0,
            total_pages=total_pages,
        )

        file = discord.File(image, filename="shop.png")

        view = ShopView(interaction.user.id, sorted_filtered)

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
        equipped_card = data.get("card", None)
        equipped_border = data.get("border", None)
        equipped_role = data.get("highlighted_role", None)

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
            equipped_card=equipped_card,
            equipped_border=equipped_border,
            equipped_role=equipped_role,
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

    @app_commands.command(name="steal", description="Steal coins from someone.")
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def steal(self, interaction: discord.Interaction, target: discord.Member):
        if target.id == interaction.user.id:
            return await interaction.response.send_message(
                "You can't steal from yourself.", ephemeral=True
            )
        user_ref = db.collection("users").document(str(interaction.user.id))
        doc = user_ref.get()
        data = doc.to_dict() if doc.exists else {}

        last_steal = data.get("last_steal")

        if last_steal:
            last_steal = last_steal.replace(tzinfo=None)
            remaining = timedelta(minutes=20) - (datetime.utcnow() - last_steal)

            if remaining.total_seconds() > 0:
                mins, secs = divmod(int(remaining.total_seconds()), 60)
                return await interaction.response.send_message(
                    f"⏳ You can steal again in {mins}m {secs}s.", ephemeral=True
                )

        target_ref = db.collection("users").document(str(target.id))
        target_doc = target_ref.get()
        target_data = target_doc.to_dict() if target_doc.exists else {}
        last_stolen_from = target_data.get("last_stolen_from")
        if last_stolen_from:
            last_stolen_from = last_stolen_from.replace(tzinfo=None)
            remaining = timedelta(minutes=20) - (datetime.utcnow() - last_stolen_from)

            if remaining.total_seconds() > 0:
                mins, secs = divmod(int(remaining.total_seconds()), 60)
                return await interaction.response.send_message(
                    f"⏳ This person cannot be stolen from again for another {mins}m {secs}s.",
                    ephemeral=True,
                )

        target_coins = target_data.get("coins", 0)
        if target_coins <= 0:
            return await interaction.response.send_message(
                "You cannot steal coins from someone who has none.", ephemeral=True
            )

        max_steal = min(target_coins, 50)
        coins = random.randint(5, max_steal)
        not_dropped = random.randint(coins - 5, coins)
        dropped = coins - not_dropped
        user_ref.update({"coins": firestore.Increment(not_dropped)})
        target_ref.update({"coins": firestore.Increment(-coins)})
        user_ref.set(
            {"last_steal": firestore.SERVER_TIMESTAMP},
            merge=True,
        )

        target_ref.set(
            {"last_stolen_from": firestore.SERVER_TIMESTAMP},
            merge=True,
        )

        return await interaction.response.send_message(
            f"{interaction.user.display_name} stole <:oathcoin:1462999179998531614>{coins} from {target.display_name}, but they dropped <:oathcoin:1462999179998531614>{dropped} in the process!"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
