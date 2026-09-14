from datetime import datetime
from typing import Any, Dict, List

import discord


def _format_ban_line(entry: Dict[str, Any]) -> str:
    discord_id = entry.get("discord_id")
    username = entry.get("username", "Unknown")
    reason = entry.get("reason", "No reason provided")
    banned_at = entry.get("banned_at")

    if banned_at and hasattr(banned_at, "strftime"):
        date_str = banned_at.strftime("%Y-%m-%d")
    else:
        date_str = "Unknown date"

    return f"**{username}** (`{discord_id}`) *at {date_str}*\n• Reason: {reason}\n"


def build_ban_list_embeds(
    bans: List[Dict[str, Any]],
    per_page: int = 10,
) -> List[discord.Embed]:
    """Builds one embed per page of bans. Always returns at least one embed."""

    if not bans:
        embed = discord.Embed(
            title="🚫 Banned Users",
            color=discord.Color.red(),
            description="No users are currently banned.",
        )
        return [embed]

    pages: List[discord.Embed] = []
    total = len(bans)
    chunks = [bans[i : i + per_page] for i in range(0, total, per_page)]
    total_pages = len(chunks)

    for page_index, chunk in enumerate(chunks, start=1):
        lines = [_format_ban_line(entry) for entry in chunk]
        embed = discord.Embed(
            title="🚫 Banned Users",
            color=discord.Color.red(),
            description="\n".join(lines),
        )
        embed.set_footer(
            text=f"Total banned users: {total} • Page {page_index}/{total_pages}"
        )
        pages.append(embed)

    return pages


class BanListPaginator(discord.ui.View):
    """View with Previous/Next buttons for paging through ban list embeds."""

    def __init__(
        self,
        embeds: List[discord.Embed],
        *,
        author_id: int | None = None,
        timeout: float = 120,
    ):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.index = 0
        self.author_id = author_id  # if set, only this user can page through it
        self._update_button_states()

    def _update_button_states(self) -> None:
        self.previous_button.disabled = self.index == 0
        self.next_button.disabled = self.index >= len(self.embeds) - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.author_id is not None and interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "You can't control this paginator.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        # message may have been deleted, so guard the edit
        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.index -= 1
        self._update_button_states()
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.index += 1
        self._update_button_states()
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)
