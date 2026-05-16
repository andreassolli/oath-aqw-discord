import asyncio
import time
from datetime import timedelta
from typing import Any, Dict, cast

import discord

from config import BADGES, SPAM_CMD_CHANNEL_ID, TICKET_LOG_CHANNEL_ID
from firebase_client import db
from user_profile.embed_badges_log import build_badge_log_embed
from user_profile.utils import (
    BADGE_CATEGORIES,
    calculate_class_count,
    calculate_epic_badges,
    calculate_founder,
    calculate_total_badges,
    calculate_weapon_count,
    calculate_whale_badges,
    check_for_ioda,
    define_whale,
    fetch_badges,
    fetch_inventory,
    get_badge_category,
    get_highest_from_category,
)


async def setup_badges(client: discord.Client):
    channel = client.get_channel(SPAM_CMD_CHANNEL_ID)

    if not channel:
        print("❌ Ticket panel channel not found. Check TICKET_CHANNEL_ID.")
        return

    await channel.send(view=BadgesLayout())


class BadgesLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        self.container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/badges.png",
                ),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164>** Apply for profile badges**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=">>> <a:sparks:1505157330055069706> Freshen up your profile card with some neat badges!\nKeep the necessary items in your inventory when applying."
                ),
                accessory=BadgesButton(),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164>** Learn more about badges**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=">>> <:star:1503523567898460311> If you wish to learn more about which badges you can get and what they are, click on '**What are badges?**'"
                ),
                accessory=GuideButton(),
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bright_separator.png",
                ),
            ),
            accent_colour=discord.Colour(7344907),
        )
        self.add_item(self.container1)


class BadgesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Apply for badges",
            style=discord.ButtonStyle.primary,
            emoji=discord.PartialEmoji(
                name="button_badges",
                id=1505158462441656450,
            ),
            custom_id="badges_button",
        )

    async def callback(self, interaction: discord.Interaction):
        layout: BadgesLayout = self.view
        self.selected_values: list[str] = [
            "Founder",
            "Whale",
            "Epic Journey",
            "Whale",
            "Class Collector",
            "51% Weapons",
        ]

        # immediate feedback
        await interaction.followup.send(
            "⏳ Applying badges, please wait...",
            ephemeral=True,
        )
        if not interaction.data:
            return await interaction.response.send_message(
                "❌ No data received.",
                ephemeral=True,
            )

        values = self.selected_values

        if not values:
            return await interaction.followup.send(
                "❌ Please select at least one badge.",
                ephemeral=True,
            )

        if not interaction.guild:
            return await interaction.followup.send(
                "❌ Must be used inside a server.",
                ephemeral=True,
            )

        # Fetch user
        user_ref = db.collection("users").document(str(interaction.user.id))
        user_doc = cast(Any, user_ref.get())
        data: Dict[str, Any] = user_doc.to_dict() or {}

        ccid = data.get("ccid", 0)

        if not ccid:
            return await interaction.followup.send(
                "❌ You must verify your AQW account first.",
                ephemeral=True,
            )

        current_discord_badges: list[str] = data.get("badges", [])
        updated_discord_badges = current_discord_badges.copy()

        passed: list[str] = []
        failed: list[str] = []
        skipped: list[str] = []

        require_badges = {"Founder", "Whale", "Epic Journey"}
        require_inventory = {"Whale", "Class Collector", "51% Weapons"}
        should_load_badges = False
        should_load_inventory = False
        for badge in values:
            if badge in require_badges:
                should_load_badges = True
            if badge in require_inventory:
                should_load_inventory = True

        if should_load_badges:
            badges = await fetch_badges(ccid)
        else:
            badges = []
        if should_load_inventory:
            inventory = await fetch_inventory(ccid)
        else:
            inventory = []

        is_founder = calculate_founder(badges)

        ioda = await check_for_ioda(inventory)

        whale_stats = calculate_whale_badges(badges)

        whale_badge = define_whale(badges, ioda)

        weapon_count = await calculate_weapon_count(inventory)

        class_count = await calculate_class_count(inventory)

        category_counts = {
            "51% Weapons": weapon_count,
            "Epic Journey": calculate_epic_badges(badges),
            "Achievement Badges": calculate_total_badges(badges),
            "Class Collector": class_count,
            "Whale": whale_stats["whale_badges"],
        }

        if "Founder" in values:
            if is_founder:
                if "AQW Founder" not in current_discord_badges:
                    updated_discord_badges.append("AQW Founder")
                    passed.append("AQW Founder")

                else:
                    skipped.append("AQW Founder")

            else:
                failed.append("AQW Founder")

        current_highest_per_category: dict[str, str] = {}

        for badge in current_discord_badges:
            category = get_badge_category(badge)

            if category:
                current_highest_per_category[category] = badge

        highest_per_category: dict[str, str | None] = {}

        for category_name, badge_map in BADGE_CATEGORIES.items():
            count = category_counts.get(category_name, 0)

            highest_per_category[category_name] = get_highest_from_category(
                badge_map,
                count,
            )

        for selected_category in values:
            if selected_category in {"Founder", "Whale"}:
                continue

            highest_allowed = highest_per_category.get(selected_category)

            if not highest_allowed:
                failed.append(selected_category)
                continue

            existing = current_highest_per_category.get(selected_category)

            if existing == highest_allowed:
                skipped.append(highest_allowed)
                continue

            # remove old tier
            updated_discord_badges = [
                b
                for b in updated_discord_badges
                if get_badge_category(b) != selected_category
            ]

            updated_discord_badges.append(highest_allowed)

            passed.append(highest_allowed)

        if whale_badge:
            existing_whale = next(
                (b for b in current_discord_badges if b.startswith("Whale")),
                None,
            )

            if existing_whale == whale_badge:
                skipped.append(whale_badge)

            else:
                updated_discord_badges = [
                    b for b in updated_discord_badges if not b.startswith("Whale")
                ]

                updated_discord_badges.append(whale_badge)

                if existing_whale:
                    passed.append(f"{existing_whale} → {whale_badge}")
                else:
                    passed.append(whale_badge)

        if updated_discord_badges != current_discord_badges:
            user_ref.set(
                {"badges": updated_discord_badges},
                merge=True,
            )

        response_lines: list[str] = []

        if passed:
            response_lines.append("✅ **Upgraded / Granted:**")
            response_lines.extend(f"• {badge}" for badge in passed)

        if skipped:
            if response_lines:
                response_lines.append("")
            response_lines.append("⏭️ **Already Owned:**")
            response_lines.extend(f"• {badge}" for badge in skipped)

        if failed:
            if response_lines:
                response_lines.append("")
            response_lines.append("❌ **Failed:**")
            response_lines.extend(f"• {badge}" for badge in failed)

        if category_counts:
            if response_lines:
                response_lines.append("")
            response_lines.append("📊 **Your Feats:**")
            response_lines.extend(
                f"• {category}: {count}" for category, count in category_counts.items()
            )

        if not response_lines:
            response_lines.append("ℹ️ No applicable badge changes.")

        log_channel = interaction.guild.get_channel(TICKET_LOG_CHANNEL_ID)

        if isinstance(log_channel, discord.TextChannel):
            embed = build_badge_log_embed(
                guild=interaction.guild,
                discord_id=interaction.user.id,
                passed=passed,
                failed=failed,
                category_counts=category_counts,
            )

            await log_channel.send(embed=embed)

        return await interaction.followup.send(
            "\n".join(response_lines),
            ephemeral=True,
        )


class GuideButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            url="https://discord.com/channels/1455651278590972019/1471212539168686345",
            style=discord.ButtonStyle.link,
            label="What are badges?",
            emoji=discord.PartialEmoji(
                name="star",
                id=1503523567898460311,
            ),
        )
