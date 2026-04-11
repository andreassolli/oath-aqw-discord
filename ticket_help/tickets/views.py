from datetime import datetime, timedelta

import discord
from firebase_admin import firestore

from config import (
    DAGE_CERTIFICATE_ID,
    DARKON_CERTIFICATE_ID,
    DRAGO_CERTIFICATE_ID,
    DRAKATH_CERTIFICATE_ID,
    EXPERIENCED_HELPER_ROLE_ID,
    GRAMIEL_CERTIFICATE_ID,
    HELPER_ROLE_ID,
    NULGATH_CERTIFICATE_ID,
    SPEAKER_CERTIFICATE_ID,
)
from firebase_client import db
from ticket_help.commands.permissions import (
    has_admin_role,
    has_oathsworn_role,
)
from ticket_help.panels.change_server_view import ServerSelectView
from ticket_help.panels.server_fetch import fetch_servers
from ticket_help.tickets.partial_complete import PartialCompleteView

from .completion_utils import finalize_ticket
from .confirm_cancel_view import ConfirmCancelView
from .confirm_complete_view import ConfirmCompleteView
from .embed_utils import build_ticket_embed
from .experienced_helper_button import SpecialBossButton
from .points import get_boss_room
from .role_claim_view import RoleClaimView
from .utils import clear_active_ticket, set_active_ticket

BOSS_TO_CERTIFICATE = {
    # "Champion Drakath": DRAKATH_CERTIFICATE_ID,
    # "Ultra Dage": DAGE_CERTIFICATE_ID,
    # "Ultra Drago": DRAGO_CERTIFICATE_ID,
    # "Ultra Darkon": DARKON_CERTIFICATE_ID,
    "Ultra Speaker": SPEAKER_CERTIFICATE_ID,
    "Ultra Gramiel": GRAMIEL_CERTIFICATE_ID,
    # "Ultra Nulgath": NULGATH_CERTIFICATE_ID,
}


class TicketActionView(discord.ui.View):
    def __init__(self, ticket_name: str, max_claims: int, room: str, bosses: list[str]):
        super().__init__(timeout=None)
        self.ticket_name = ticket_name
        self.max_claims = max_claims
        self.room = room
        self.bosses = bosses

        if any(boss in ["Ultra Speaker", "Ultra Gramiel"] for boss in bosses):
            doc_ref = db.collection("tickets").document(ticket_name)
            doc = doc_ref.get()

            experienced_only = False
            if doc.exists:
                experienced_only = doc.to_dict().get("experienced_only", False)

            self.add_item(SpecialBossButton(ticket_name, self, experienced_only))

    async def _update_ticket_embed(self, interaction: discord.Interaction):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()
        if not doc.exists:
            return

        ticket_data = doc.to_dict()
        message_id = ticket_data.get("message_id")
        if not message_id:
            return

        try:
            message = await interaction.channel.fetch_message(message_id)
            claimer_roles = ticket_data.get("claimer_roles", {})
            total_kills = ticket_data.get("total_kills", "0")
            embed = build_ticket_embed(
                requester_id=ticket_data["user_id"],
                bosses=ticket_data["bosses"],
                points=ticket_data["points"],
                username=ticket_data["username"],
                room=ticket_data["room"],
                max_claims=ticket_data["max_claims"],
                claimers=ticket_data["claimers"],
                guild=interaction.guild,
                type=ticket_data["type"],
                server=ticket_data["server"],
                total_kills=total_kills,
                claimer_roles=claimer_roles,
            )

            await message.edit(embed=embed, view=self)

        except discord.NotFound:
            pass

    @discord.ui.button(
        label="👊 Claim or unclaim", style=discord.ButtonStyle.success, row=3
    )
    async def claim_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True)

        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.followup.send(
                "❌ Ticket data not found.", ephemeral=True
            )

        data = doc.to_dict()
        claimers = data.get("claimers", [])

        requester_id = data.get("user_id")
        is_requester = interaction.user.id == requester_id
        if interaction.user.id in claimers:
            claimers.remove(interaction.user.id)

            roles = data.get("claimer_roles", {})

            roles.pop(str(interaction.user.id), None)

            doc_ref.update(
                {
                    "claimers": claimers,
                    "claimer_roles": roles,
                }
            )

            clear_active_ticket(interaction.user.id, self.ticket_name)

            await self._update_ticket_embed(interaction)

            await interaction.channel.send(
                f"🔁 {interaction.user.mention} unclaimed this ticket "
                f"({len(claimers) + 1}/{self.max_claims + 1})"
            )
            return

        if len(claimers) >= self.max_claims:
            return await interaction.followup.send(
                "🚫 No more spots available.", ephemeral=True
            )

        user_ref = db.collection("users").document(str(interaction.user.id))
        user_doc = user_ref.get()
        active_ticket = (
            user_doc.to_dict().get("active_ticket") if user_doc.exists else None
        )
        if user_doc.exists and active_ticket and active_ticket != self.ticket_name:
            return await interaction.followup.send(
                "🚫 You are already helping on another ticket.", ephemeral=True
            )

        if is_requester and "Grim Challenge" not in self.bosses:
            return await interaction.followup.send(
                "🚫 Ticket creator cannot claim their own ticket.",
                ephemeral=True,
            )

        experienced_only = data.get("experienced_only", False)

        member = interaction.user
        guild = interaction.guild

        helper_role = guild.get_role(HELPER_ROLE_ID)

        has_helper = helper_role in member.roles if helper_role else False

        needed_certificates = []
        for boss in self.bosses:
            if boss in BOSS_TO_CERTIFICATE:
                needed_certificates.append(BOSS_TO_CERTIFICATE[boss])

        member_role_ids = {role.id for role in member.roles}

        if experienced_only:
            for cert in needed_certificates:
                if cert not in member_role_ids:
                    return await interaction.followup.send(
                        "🚫 You need a **Certification** for one or more of the bosses in this ticket.",
                        ephemeral=True,
                    )
        else:
            if not has_helper:
                return await interaction.followup.send(
                    "🚫 You must be a helper to claim this ticket.",
                    ephemeral=True,
                )
        if "Grim Challenge" in self.bosses:
            roles = data.get("claimer_roles", {})

            view = RoleClaimView(
                ticket_name=self.ticket_name,
                user_id=interaction.user.id,
                parent_view=self,
                roles=roles,
                is_requester=is_requester,
            )

            return await interaction.followup.send(
                "Select your role before claiming:",
                view=view,
                ephemeral=True,
            )

        claimers.append(interaction.user.id)
        doc_ref.update({"claimers": claimers})
        set_active_ticket(interaction.user.id, self.ticket_name)

        await self._update_ticket_embed(interaction)

        await interaction.channel.send(
            f"✅ {interaction.user.mention} claimed this ticket "
            f"({len(claimers) + 1}/{self.max_claims + 1})"
        )

        lines = []
        for boss in self.bosses:
            custom_tickets = {"spamming", "testing", "until drop"}
            if data.get("type") in custom_tickets:
                rooms = boss
            else:
                rooms = get_boss_room(boss)

            if not rooms:
                continue

            # Split multiple rooms by comma
            room_list = [r.strip() for r in rooms.split(",")]

            for room in room_list:
                lines.append(f"```/join {room}-{self.room}```")

        rooms_text = "".join(lines)

        await interaction.followup.send(
            f"📋 **Room codes:**\n{rooms_text}", ephemeral=True
        )

    @discord.ui.button(
        label="📋 Get room codes", style=discord.ButtonStyle.secondary, row=3
    )
    async def copy_room(self, interaction: discord.Interaction, _):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.followup.send(
                "❌ Ticket data not found.", ephemeral=True
            )

        data = doc.to_dict()
        claimers = data.get("claimers", [])

        requester_id = data.get("user_id")
        if interaction.user.id not in claimers and interaction.user.id != requester_id:
            return await interaction.response.send_message(
                "❌ You must claim this ticket first!", ephemeral=True
            )

        lines = []

        for boss in self.bosses:
            custom_tickets = {"spamming", "testing", "until drop"}
            if data.get("type") in custom_tickets:
                rooms = boss
            else:
                rooms = get_boss_room(boss)

            if not rooms:
                continue

            # Split multiple rooms by comma
            room_list = [r.strip() for r in rooms.split(",")]

            for room in room_list:
                lines.append(f"```/join {room}-{self.room}```")

        rooms_text = "".join(lines)

        await interaction.response.send_message(
            f"📋 **Room codes:**\n{rooms_text}", ephemeral=True
        )

    @discord.ui.button(
        label="🎉 Complete Ticket", style=discord.ButtonStyle.success, row=1
    )
    async def complete_ticket(self, interaction: discord.Interaction, _):
        await interaction.response.defer(ephemeral=True)

        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.followup.send(
                "❌ Ticket data not found.", ephemeral=True
            )

        data = doc.to_dict()

        if data.get("status") in ("completing", "completed"):
            return await interaction.followup.send(
                "⚠️ This ticket has already been completed.", ephemeral=True
            )

        requester_id = data.get("user_id")
        is_requester = interaction.user.id == requester_id
        is_admin = has_admin_role(interaction)
        is_oathsworn = has_oathsworn_role(interaction)

        if not (is_requester or is_admin or is_oathsworn):
            return await interaction.followup.send(
                "🚫 Only the ticket creator or an admin can complete this ticket.",
                ephemeral=True,
            )

        claimers = data.get("claimers", [])
        if len(claimers) == 0:
            return await interaction.followup.send(
                "⚠️ You cannot complete a ticket with no helpers.",
                ephemeral=True,
            )

        max_claims = data.get("max_claims", 1)
        points = data.get("points", 1)

        if len(claimers) < max_claims:
            view = ConfirmCompleteView(self.ticket_name)

            await interaction.followup.send(
                f"⚠️ **This ticket only has {len(claimers)} helper(s).** "
                "Make sure the whole ticket is finished before completing.\n"
                "Completing unfinished tickets is against the rules. "
                "Is the ticket **finished**?\n",
                ephemeral=True,
                view=view,
            )
            return

        await finalize_ticket(
            interaction=interaction,
            ticket_name=self.ticket_name,
            ticket_data=data,
        )

    @discord.ui.button(
        label="📝 Partial Complete", style=discord.ButtonStyle.primary, row=1
    )
    async def partially_complete_ticket(self, interaction: discord.Interaction, _):
        await interaction.response.defer(ephemeral=True)

        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.followup.send(
                "❌ Ticket data not found.", ephemeral=True
            )

        data = doc.to_dict()
        if data.get("type") in {"other bosses", "spamming", "testing", "until drop"}:
            return await interaction.followup.send(
                "⚠️ Partial completion is not available for this ticket type.",
                ephemeral=True,
            )

        if data.get("status") in ("completing", "completed"):
            return await interaction.followup.send(
                "⚠️ This ticket has already been completed.", ephemeral=True
            )

        requester_id = data.get("user_id")
        is_requester = interaction.user.id == requester_id
        is_admin = has_admin_role(interaction)
        is_oathsworn = has_oathsworn_role(interaction)

        if not (is_requester or is_admin or is_oathsworn):
            return await interaction.followup.send(
                "🚫 Only the ticket creator or an admin can complete this ticket.",
                ephemeral=True,
            )

        points = data.get("points", 1)
        claimers = data.get("claimers", [])
        if len(claimers) == 0:
            return await interaction.followup.send(
                "⚠️ You cannot complete a ticket with no helpers.",
                ephemeral=True,
            )

        view = PartialCompleteView(self.ticket_name, self.bosses)

        await interaction.followup.send(
            "📝 Select which bosses were completed:",
            view=view,
            ephemeral=True,
        )

    @discord.ui.button(label="🗑️ Cancel Ticket", style=discord.ButtonStyle.danger, row=1)
    async def cancel_ticket(self, interaction: discord.Interaction, _):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.response.send_message(
                "❌ Ticket data not found.", ephemeral=True
            )

        data = doc.to_dict()
        requester_id = data.get("user_id")
        is_requester = interaction.user.id == requester_id
        is_admin = has_admin_role(interaction)
        is_oathsworn = has_oathsworn_role(interaction)

        if not (is_requester or is_admin or is_oathsworn):
            return await interaction.response.send_message(
                "🚫 Only the ticket creator or an admin can cancel this ticket.",
                ephemeral=True,
            )

        view = ConfirmCancelView(self.ticket_name, data)

        await interaction.response.send_message(
            "⚠️ **Are you sure you want to cancel this ticket?**\n"
            "This action cannot be undone.",
            ephemeral=True,
            view=view,
        )

    @discord.ui.button(
        label="🌐 Change Server", style=discord.ButtonStyle.secondary, row=2
    )
    async def change_server(self, interaction: discord.Interaction, _):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.response.send_message(
                "❌ Ticket data not found.", ephemeral=True
            )

        data = doc.to_dict()

        requester_id = data.get("user_id")
        is_requester = interaction.user.id == requester_id
        is_admin = has_admin_role(interaction)
        is_oathsworn = has_oathsworn_role(interaction)

        # 🔒 SAME PERMISSIONS AS COMPLETE/CANCEL
        if not (is_requester or is_admin or is_oathsworn):
            return await interaction.response.send_message(
                "🚫 Only the ticket creator or an admin can change the server.",
                ephemeral=True,
            )

        servers = await fetch_servers()

        view = ServerSelectView(self.ticket_name, servers, parent_view=self)

        await interaction.response.send_message(
            "🌐 Select a new server:", view=view, ephemeral=True
        )

    @discord.ui.button(
        label="📣 Ping Helpers", style=discord.ButtonStyle.primary, row=2
    )
    async def ping_helpers(self, interaction: discord.Interaction, _):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.response.send_message(
                "❌ Ticket data not found.", ephemeral=True
            )

        data = doc.to_dict()

        requester_id = data.get("user_id")
        is_admin = has_admin_role(interaction)

        if interaction.user.id != requester_id and not is_admin:
            return await interaction.response.send_message(
                "🚫 Only the ticket creator or an admin can ping helpers.",
                ephemeral=True,
            )

        now = datetime.utcnow()
        last_ping = data.get("last_helper_ping")

        if last_ping:
            last_ping_dt = last_ping.replace(tzinfo=None)
            remaining = timedelta(minutes=10) - (now - last_ping_dt)

            if remaining.total_seconds() > 0:
                mins, secs = divmod(int(remaining.total_seconds()), 60)
                return await interaction.response.send_message(
                    f"⏳ Helpers were pinged recently.\n"
                    f"Try again in **{mins}m {secs}s**.",
                    ephemeral=True,
                )

        helper_role = interaction.guild.get_role(HELPER_ROLE_ID)

        if not helper_role:
            return await interaction.response.send_message(
                "❌ Helper role not found.", ephemeral=True
            )

        doc_ref.update({"last_helper_ping": firestore.SERVER_TIMESTAMP})

        await interaction.response.send_message(
            "📣 Helpers have been pinged!", ephemeral=True
        )

        await interaction.channel.send(
            f"{helper_role.mention}\n⚠️ **More helpers needed for this ticket!**",
            allowed_mentions=discord.AllowedMentions(roles=True),
        )
