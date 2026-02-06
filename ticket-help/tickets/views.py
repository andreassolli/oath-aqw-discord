import discord
from firebase_admin import firestore
from tickets.confirm_cancel_view import ConfirmCancelView
from config import HELPER_ROLE_ID, ADMIN_ROLE_ID, WEEKLY_REQUESTER_CAP
from dashboard.updater import update_dashboard
from firebase_client import db
from tickets.ids import get_next_ticket_id
from tickets.utils import set_active_ticket, clear_active_ticket, get_week_start
from tickets.logging import log_ticket_event
from commands.permissions import has_admin_role, has_helper_role, has_oathsworn_role
from tickets.embed_utils import build_ticket_embed
from datetime import datetime, timedelta
from tickets.embed_logging import build_logging_embed
from tickets.confirm_complete_view import ConfirmCompleteView
from utils.ticket import can_claim_ticket

class TicketActionView(discord.ui.View):
    def __init__(self, ticket_name: str, max_claims: int, room: str):
        super().__init__(timeout=None)
        self.ticket_name = ticket_name
        self.max_claims = max_claims
        self.room = room

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
                server=ticket_data["server"]
            )

            await message.edit(embed=embed, view=self)

        except discord.NotFound:
            pass

    @discord.ui.button(label="👊 Claim or unclaim", style=discord.ButtonStyle.success)
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

        if interaction.user.id in claimers:
            claimers.remove(interaction.user.id)
            doc_ref.update({"claimers": claimers})
            clear_active_ticket(interaction.user.id, self.ticket_name)

            await self._update_ticket_embed(interaction)

            await interaction.channel.send(
                f"🔁 {interaction.user.mention} unclaimed this ticket "
                f"({len(claimers)+1}/{self.max_claims+1})"
            )
            return

        # Check for if the user:
        # 1. Is not the requester
        # 2. Is a helper
        # 3. Have no active ticket
        can_claim_ticket(claimers, self.max_claims, interaction, requester_id)

        claimers.append(interaction.user.id)
        doc_ref.update({"claimers": claimers})
        set_active_ticket(interaction.user.id, self.ticket_name)

        await self._update_ticket_embed(interaction)

        await interaction.channel.send(
            f"✅ {interaction.user.mention} claimed this ticket "
            f"({len(claimers)+1}/{self.max_claims+1})"
        )


    @discord.ui.button(label="📋 Copy Room", style=discord.ButtonStyle.secondary)
    async def copy_room(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(
            f"📋 **Room code:**\n```{self.room}```",
            ephemeral=True
        )

    @discord.ui.button(label="🎉 Complete Ticket", style=discord.ButtonStyle.primary)
    async def complete_ticket(self, interaction: discord.Interaction, _):
        await interaction.response.defer(ephemeral=True)

        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.followup.send(
                "❌ Ticket data not found.",
                ephemeral=True
            )

        data = doc.to_dict()

        if data.get("status") in ("completing", "completed"):
            return await interaction.followup.send(
                "⚠️ This ticket has already been completed.",
                ephemeral=True
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
        max_claims = data.get("max_claims", 1)

        if len(claimers) < max_claims:
            view = ConfirmCompleteView(self.ticket_name)

            await interaction.followup.send(
                f"⚠️ **This ticket only has {len(claimers)} helper(s). "
                "Make sure the whole ticket is finished before completing.\n"
                "Completing unfinished tickets is against the rules. "
                "Is the ticket **finished**?\n",
                ephemeral=True,
                view=view
            )
            return

        doc_ref.update({
            "status": "completing",
            "closed_by": interaction.user.id,
            "closed_at": firestore.SERVER_TIMESTAMP,
        })

        claimers = [uid for uid in claimers if uid != requester_id]

        for user_id in claimers:
            user_ref = db.collection("users").document(str(user_id))
            clear_active_ticket(user_id, self.ticket_name)

            member = await interaction.guild.fetch_member(user_id)
            username = member.display_name

            if user_ref.get().exists:
                user_ref.update({
                    "username": username,
                    "points": firestore.Increment(points),
                    "tickets_claimed": firestore.Increment(1),
                })
            else:
                user_ref.set({
                    "username": username,
                    "points": points,
                    "tickets_claimed": 1
                })

        user_ref = db.collection("users").document(str(requester_id))
        user_doc = user_ref.get()

        amount_bosses = len(data.get("bosses", []))
        ticket_type = data.get("type")

        MULTIPLIERS = {
            "testing": 0,
            "spamming": 2,
            "7 man bosses": 2,
        }

        multiplier = MULTIPLIERS.get(ticket_type, 1)
        user_point_reward = multiplier * amount_bosses

        now = datetime.utcnow()
        week_start = get_week_start(now)

        weekly_points = 0
        weekly_reset = None

        if user_doc.exists:
            user_data = user_doc.to_dict()
            weekly_points = user_data.get("weekly_points", 0)
            weekly_reset = user_data.get("weekly_points_reset")

        if not weekly_reset or weekly_reset.replace(tzinfo=None) < week_start:
            weekly_points = 0
            weekly_reset = week_start

        remaining = max(0, WEEKLY_REQUESTER_CAP - weekly_points)
        final_reward = min(user_point_reward, remaining)

        updates = {
            "weekly_points": weekly_points + final_reward,
            "weekly_points_reset": weekly_reset,
        }

        if final_reward > 0:
            updates["points"] = firestore.Increment(final_reward)

        if user_doc.exists:
            user_ref.update(updates)
        else:
            updates["points"] = final_reward
            updates["tickets_claimed"] = 1
            user_ref.set(updates)

        clear_active_ticket(requester_id, self.ticket_name)

        embed = build_logging_embed(
            requester_id=requester_id,
            bosses=data.get("bosses", []),
            username=data.get("username", "—"),
            max_claims=data.get("max_claims", 0),
            claimers=claimers,
            guild=interaction.guild,
            type=data.get("type", "unknown"),
            created_at=data.get("created_at"),
            closer_id=interaction.user.id,
            cancelled=False,
            points=points,
        )

        doc_ref.update({"status": "completed"})

        await interaction.followup.send("🎉 Ticket completed.", ephemeral=True)
        await log_ticket_event(interaction.client, embed=embed)
        await update_dashboard(interaction.client)
        await interaction.channel.delete()


    @discord.ui.button(label="📣 Ping Helpers", style=discord.ButtonStyle.primary)
    async def ping_helpers(self, interaction: discord.Interaction, _):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.response.send_message(
                "❌ Ticket data not found.",
                ephemeral=True
            )

        data = doc.to_dict()

        requester_id = data.get("user_id")
        is_admin = has_admin_role(interaction)

        if interaction.user.id != requester_id and not is_admin:
            return await interaction.response.send_message(
                "🚫 Only the ticket creator or an admin can ping helpers.",
                ephemeral=True
            )

        now = datetime.utcnow()
        last_ping = data.get("last_helper_ping")

        if last_ping:
            last_ping_dt = last_ping.replace(tzinfo=None)
            remaining = timedelta(minutes=5) - (now - last_ping_dt)

            if remaining.total_seconds() > 0:
                mins, secs = divmod(int(remaining.total_seconds()), 60)
                return await interaction.response.send_message(
                    f"⏳ Helpers were pinged recently.\n"
                    f"Try again in **{mins}m {secs}s**.",
                    ephemeral=True
                )

        helper_role = interaction.guild.get_role(HELPER_ROLE_ID)
        if not helper_role:
            return await interaction.response.send_message(
                "❌ Helper role not found.",
                ephemeral=True
            )

        doc_ref.update({
            "last_helper_ping": firestore.SERVER_TIMESTAMP
        })

        await interaction.response.send_message(
            "📣 Helpers have been pinged!",
            ephemeral=True
        )

        await interaction.channel.send(
            f"{helper_role.mention}\n"
            f"⚠️ **More helpers needed for this ticket!**",
            allowed_mentions=discord.AllowedMentions(roles=True)
        )


    @discord.ui.button(label="🗑️ Cancel Ticket", style=discord.ButtonStyle.danger)
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

        if not (is_requester or is_admin):
            return await interaction.response.send_message(
                "🚫 Only the ticket creator or an admin can cancel this ticket.",
                ephemeral=True,
            )


        view = ConfirmCancelView(self.ticket_name, data)

        await interaction.response.send_message(
            "⚠️ **Are you sure you want to cancel this ticket?**\n"
            "This action cannot be undone.",
            ephemeral=True,
            view=view
        )
