import discord
from firebase_admin import firestore
from firebase_client import db
from tickets.ids import get_next_ticket_id
from tickets.views import TicketActionView
from config import HELPER_ROLE_ID, ADMIN_ROLE_ID
from config import TICKET_CATEGORY_ID
from tickets.embed_utils import build_ticket_embed
from tickets.utils import set_active_ticket, clear_active_ticket
from tickets.confirm_complete_view import ConfirmCompleteView
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
                required=True
            )
            self.add_item(self.bosses_input)

        self.username = discord.ui.TextInput(
            label="Username",
            required=True
        )

        self.room = discord.ui.TextInput(
            label="Room",
            placeholder="Private rooms need 4+ digits",
            required=True
        )

        self.add_item(self.username)
        self.add_item(self.room)

        if self.type in {"other bosses", "spamming", "testing"}:
            self.max_claims = discord.ui.TextInput(
                label="Maximum helpers",
                placeholder="Digit between 1 and 20",
                required=True
            )
            self.add_item(self.max_claims)
        else:
            self.max_claims = None

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        type_doc = db.collection("point_rules").document(self.type).get()
        type_data = type_doc.to_dict() or {}
        six_helper_bosses = ["Astral Shrine", "Grim Challenge", "Apex Azalith", "The Beast", "Void Trio", "Lich King", "Deimos", "Azalith", "Kathool Depths"]

        role = interaction.guild.get_role(HELPER_ROLE_ID)
        if self.max_claims is not None:
            max_claims_value = int(self.max_claims.value)
        elif any(
            bossA in bossB
            for bossA in six_helper_bosses
            for bossB in self._preset_bosses
        ):
            max_claims_value = 6
        else:
            max_claims_value = 3

        ticket_id = get_next_ticket_id()
        name = f"「🔖」ticket-{ticket_id:03d}"
        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)

        overwrites = get_overwrites(interaction)

        channel = await interaction.guild.create_text_channel(
            name=name,
            category=category,
            overwrites=overwrites,
        )

        if self.type in {"other bosses", "spamming", "testing"}:
            bosses = [
                b.strip()
                for b in self.bosses_input.value.split(",")
                if b.strip()
            ]
            points = 1 * len(bosses)
        else:
            bosses = self._preset_bosses

            amount = len(bosses)

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

        db.collection("tickets").document(name).set({
            "ticket_id": ticket_id,
            "channel_id": channel.id,
            "user_id": interaction.user.id,
            "bosses": bosses,
            "points": points,
            "max_claims": max_claims_value,
            "claimers": [],
            "username": self.username.value,
            "room": self.room.value,
            "status": "open",
            "type": self.type,
            "server": self.server,
            "created_at": firestore.SERVER_TIMESTAMP,
            "reping_helpers": True,
            "reminder_sent": False,
            "auto_closed": False,
        })

        embed = build_ticket_embed(
            requester_id=interaction.user.id,
            bosses=bosses,
            points=points,
            username=self.username.value,
            room=self.room.value,
            max_claims=max_claims_value,
            claimers=[],
            guild=interaction.guild,
            type=self.type,
            server=self.server,
        )
        allowed_mentioning = discord.AllowedMentions(
            users=True,
            roles=True,
            everyone=False
        )


        message = await channel.send(
            embed=embed,
            view=TicketActionView(
                ticket_name=name,
                max_claims=max_claims_value,
                room=self.room.value,
            ),
            allowed_mentions=allowed_mentioning,
        )

        db.collection("tickets").document(name).update({
            "message_id": message.id
        })

        set_active_ticket(interaction.user.id, name)
        await interaction.followup.send(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True
        )

        try:
            await message.pin(reason="Ticket information")
        except discord.Forbidden:
            # Bot is missing 'Manage Messages'
            pass
