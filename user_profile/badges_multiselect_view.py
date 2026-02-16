from typing import Any, Dict, cast

import discord

from config import BADGES, TICKET_LOG_CHANNEL_ID
from firebase_client import db

from .badges_multiselect import BadgesMultiSelect
from .embed_badges_log import build_badge_log_embed
from .utils import (
    BADGE_CATEGORIES,
    define_whale,
    founder_check,
    get_badge_category,
    get_category_counts,
    get_highest_from_category,
)


class BadgesMultiSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.selected_values: list[str] = []
        self.select = BadgesMultiSelect(BADGES)
        self.add_item(self.select)

    @discord.ui.button(
        label="📝 Apply for badges", style=discord.ButtonStyle.primary, row=1
    )
    async def apply_for_badges(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button["BadgesMultiSelectView"],
    ):

        interaction_data = interaction.data
        if not interaction_data:
            return await interaction.response.send_message(
                "❌ No data received from the interaction.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True)

        values = self.selected_values

        if not values:
            return await interaction.response.send_message(
                "❌ Please select at least one badge.",
                ephemeral=True,
            )

        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ This can only be used inside a server.",
                ephemeral=True,
            )

        user_ref = db.collection("users").document(str(interaction.user.id))
        user_doc = cast(Any, user_ref.get())
        data: Dict[str, Any] = user_doc.to_dict() or {}

        ccid = data.get("ccid", 0)
        if ccid == 0:
            return await interaction.response.send_message(
                "❌ You need to verify your AQW account before applying for badges.",
                ephemeral=True,
            )

        current_badges: list[str] = data.get("badges", [])
        updated_badges = current_badges.copy()

        passed: list[str] = []
        failed: list[str] = []
        skipped: list[str] = []

        if "Founder" in values:
            is_founder = await founder_check(ccid)

            if is_founder:
                if "AQW Founder" not in current_badges:
                    updated_badges.append("AQW Founder")
                    passed.append("AQW Founder")
                else:
                    skipped.append("AQW Founder")
            else:
                failed.append("AQW Founder")

        current_highest_per_category: dict[str, str] = {}

        for badge in current_badges:
            category = get_badge_category(badge)
            if category:
                current_highest_per_category[category] = badge

        category_counts = await get_category_counts(ccid)

        highest_per_category: dict[str, str | None] = {}

        for category_name, badge_map in BADGE_CATEGORIES.items():
            count = category_counts.get(category_name, 0)
            highest = get_highest_from_category(badge_map, count)
            highest_per_category[category_name] = highest

        for selected_badge in values:
            if selected_badge in {"Founder", "Whale"}:
                continue

            category = selected_badge
            highest_allowed = highest_per_category.get(category)

            if not highest_allowed:
                failed.append(selected_badge)
                continue

            existing = current_highest_per_category.get(category)

            if existing == highest_allowed:
                skipped.append(highest_allowed)
                continue

            passed.append(highest_allowed)

            # Remove old tier
            updated_badges = [
                b for b in updated_badges if get_badge_category(b) != category
            ]

            updated_badges.append(highest_allowed)

        whale_badge = await define_whale(ccid)
        print(f"Determined whale badge: {whale_badge}")

        if whale_badge:
            existing_whale = next(
                (b for b in current_badges if b.startswith("Whale")),
                None,
            )

            if existing_whale == whale_badge:
                skipped.append(whale_badge)

            else:
                # Remove old Whale tier(s)
                updated_badges = [
                    b for b in updated_badges if not b.startswith("Whale")
                ]

                updated_badges.append(whale_badge)

                if existing_whale:
                    passed.append(f"{existing_whale} → {whale_badge}")
                else:
                    passed.append(whale_badge)

        if updated_badges != current_badges:
            user_ref.set({"badges": updated_badges}, merge=True)

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
            response_lines.append("ℹ️ No applicable badge checks found.")

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

        return await interaction.response.send_message(
            "\n".join(response_lines),
            ephemeral=True,
        )
