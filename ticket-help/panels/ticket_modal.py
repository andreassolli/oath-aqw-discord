import random

import discord
from config import (
    ADMIN_ROLE_ID,
    GUIDE_CHANNEL_ID,
    HELPER_ROLE_ID,
    TICKET_CATEGORY_ID,
    spam_points,
)
from firebase_admin import firestore
from firebase_client import db
from tickets.confirm_complete_view import ConfirmCompleteView
from tickets.embed_utils import build_ticket_embed
from tickets.ids import get_next_ticket_id
from tickets.utils import clear_active_ticket, find_guide_threads, set_active_ticket
from tickets.views import TicketActionView
from utils.ticket import get_overwrites


class CreateTicketModal(discord.ui.Modal):
    def __init__(self, ticket_type: str, server: str, bosses: list[str]):
        super().__init__(title=f"Create {ticket_type.capitalize()} Ticket")

        self.type = ticket_type
        self.server = server

        self._preset_bosses = bosses

        self.bosses_input: discord.ui.TextInput | None = None

        if self.type in {"other bosses", "spamming", "testing"}:
            self.bosses_input = discord.ui.TextInput(
                label="List bosses (comma-separated)",
                placeholder="Boss1, Boss2, Boss3",
                required=True,
            )
            self.add_item(self.bosses_input)

        self.username = discord.ui.TextInput(label="Username", required=True)

        # if self.type in {"other bosses", "spamming", "testing"}:
        #    self.room_input = discord.ui.TextInput(
        #        label="Room",
        #        placeholder="Private rooms need 4+ digits",
        #        required=True
        #    )
        #    self.add_item(self.room_input)
        #    self.room = None
        # else:
        self.room = random.randint(11111, 99999)
        self.room_input = None

        self.add_item(self.username)

        if self.type in {"other bosses", "spamming", "testing"}:
            self.max_claims_input = discord.ui.TextInput(
                label="Maximum helpers",
                placeholder="Digit between 1 and 20",
                required=True,
            )
            self.add_item(self.max_claims_input)
        else:
            self.max_claims_input = None
            self.max_claims = None

        if self.type == "spamming":
            self.total_kills_input = discord.ui.TextInput(
                label="Total kills",
                placeholder="Digit between 1 and 500",
                required=True,
            )
            self.add_item(self.total_kills_input)
        else:
            self.total_kills_input = None
            self.total_kills = 1

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            room_value = int(self.room_input.value) if self.room_input else self.room
        except ValueError:
            await interaction.response.send_message(
                "❌ Room must be a number.", ephemeral=True
            )
            return

        if self.total_kills_input:
            try:
                total_kills_value = int(self.total_kills_input.value)
            except ValueError:
                return await interaction.response.send_message(
                    "❌ Total kills must be a number.", ephemeral=True
                )
        else:
            total_kills_value = 1

        type_doc = db.collection("point_rules").document(self.type).get()
        type_data = type_doc.to_dict() or {}
        six_helper_bosses = [
            "Astral Shrine",
            "Grim Challenge",
            "Apex Azalith",
            "The Beast",
            "Void Trio",
            "Lich King",
            "Deimos",
            "Azalith",
            "Kathool Depths",
        ]

        if self.max_claims_input:
            max_claims_value = int(self.max_claims_input.value)
        elif any(
            bossA in bossB
            for bossA in six_helper_bosses
            for bossB in self._preset_bosses
        ):
            max_claims_value = 6
        else:
            max_claims_value = 3

        ticket_id = get_next_ticket_id()
        channel_name = f"「🔖」ticket-{ticket_id:03d}"
        ticket_name = f"ticket-{ticket_id:03d}"
        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)

        overwrites = get_overwrites(interaction)

        channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
        )

        if self.type in {"other bosses", "spamming", "testing"}:
            bosses = [boss.strip() for boss in self.bosses_input.value.split(",")]
            start = 0
            end = len(spam_points) - 1
            mid = (start + end) // 2
            while start < end:
                mid = (start + end) // 2
                if spam_points[mid] > total_kills_value:
                    end = mid - 1
                elif spam_points[mid] < total_kills_value:
                    start = mid + 1
                else:
                    break

            points = start + 1
        else:
            bosses = self._preset_bosses

            type_ref = db.collection("point_rules")
            points = 0
            legion_boss_counter = 0
            legion_bosses = ["The Beast", "Deimos", "Legion Lich Lord"]

            for boss in bosses:
                if boss in legion_bosses:
                    legion_boss_counter += 1
                    continue

                boss_doc = type_ref.document(boss).get()
                boss_data = boss_doc.to_dict() if boss_doc.exists else {}

                points += int(boss_data.get("points", 1))

            if legion_boss_counter > 1:
                legion_doc = type_ref.document("Legion Daily").get()
                legion_data = legion_doc.to_dict() if legion_doc.exists else {}

                points += int(legion_data.get("points", 1))

        db.collection("tickets").document(ticket_name).set(
            {
                "ticket_id": ticket_id,
                "channel_id": channel.id,
                "user_id": interaction.user.id,
                "bosses": bosses,
                "points": points,
                "max_claims": max_claims_value,
                "claimers": [],
                "username": self.username.value,
                "room": room_value,
                "status": "open",
                "type": self.type,
                "server": self.server,
                "created_at": firestore.SERVER_TIMESTAMP,
                "reping_helpers": True,
                "reminder_sent": False,
                "auto_closed": False,
                "total_kills": total_kills_value,
            }
        )

        embed = build_ticket_embed(
            requester_id=interaction.user.id,
            bosses=bosses,
            points=points,
            username=self.username.value,
            room=str(room_value),
            max_claims=max_claims_value,
            claimers=[],
            guild=interaction.guild,
            type=self.type,
            server=self.server,
            total_kills=str(total_kills_value),
        )

        allowed_mentioning = discord.AllowedMentions(
            users=True, roles=True, everyone=False
        )

        message = await channel.send(
            embed=embed,
            view=TicketActionView(
                ticket_name=ticket_name,
                max_claims=max_claims_value,
                room=str(room_value),
                bosses=bosses,
            ),
            allowed_mentions=allowed_mentioning,
        )

        guide_threads = await find_guide_threads(
            guild=interaction.guild,
            guide_channel_id=GUIDE_CHANNEL_ID,
            bosses=bosses,
        )

        if guide_threads:
            lines = []
            for boss, thread in guide_threads.items():
                lines.append(f"• **{boss}** → {thread.mention}")

            await channel.send("📘 **Relevant Guides**\n" + "\n".join(lines))

        db.collection("tickets").document(ticket_name).update(
            {"message_id": message.id}
        )

        set_active_ticket(interaction.user.id, ticket_name)
        await interaction.followup.send(
            f"✅ Ticket created: {channel.mention}", ephemeral=True
        )

        try:
            await message.pin(reason="Ticket information")
        except discord.Forbidden:
            # Bot is missing 'Manage Messages'
            pass
