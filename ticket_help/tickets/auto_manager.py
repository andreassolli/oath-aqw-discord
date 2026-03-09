from datetime import datetime, timedelta, timezone

import discord
from discord.ext import tasks
from firebase_admin import firestore

from firebase_client import db
from ticket_help.dashboard.updater import update_dashboard
from ticket_help.tickets.embed_logging import build_logging_embed
from ticket_help.tickets.logging import log_ticket_event
from ticket_help.tickets.utils import clear_active_ticket

REMINDER_AFTER = timedelta(minutes=45)
AUTOCLOSE_AFTER = timedelta(hours=5)


class TicketAutoManager:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.ticket_watcher.start()

    def cog_unload(self):
        self.ticket_watcher.cancel()

    @tasks.loop(minutes=1)
    async def ticket_watcher(self):
        now = datetime.now(timezone.utc)

        tickets = db.collection("tickets").where("status", "==", "open").stream()

        for ticket in tickets:
            data = ticket.to_dict()
            created_at = data.get("created_at")

            if not created_at:
                continue

            age = now - created_at.replace(tzinfo=timezone.utc)
            channel = self.bot.get_channel(data["channel_id"])

            if not channel:
                continue

            # 🔔 30-minute reminder
            if age >= REMINDER_AFTER and not data.get("reminder_sent", False):
                try:
                    user = await self.bot.fetch_user(data["user_id"])

                    claimers = data.get("claimers", [])
                    max_claims = data.get("max_claims", 0)

                    messages = [
                        f"⏰ {user.mention} **Reminder:**",
                        "Please complete or close this ticket if it’s done.",
                    ]

                    await channel.send("\n".join(messages))

                except Exception:
                    pass

                ticket.reference.update({"reminder_sent": True})

            # 🔒 12-hour autoclose
            if age >= AUTOCLOSE_AFTER:
                await self.auto_close(ticket, data, channel)

    async def auto_close(self, ticket, data, channel):
        guild = channel.guild

        requester_id = data["user_id"]
        claimers = data.get("claimers", [])

        # ✅ Clear active ticket for requester
        clear_active_ticket(requester_id, ticket.id)

        # ✅ Clear active tickets for helpers
        for user_id in claimers:
            clear_active_ticket(user_id, ticket.id)

        # Build display names
        requester_member = guild.get_member(requester_id)
        requester_display = (
            requester_member.display_name
            if requester_member
            else f"User {requester_id}"
        )

        helper_displays = {}
        for user_id in claimers:
            member = guild.get_member(user_id)
            helper_displays[user_id] = (
                member.display_name if member else f"User {user_id}"
            )

        # ✅ Build logging embed
        embed = build_logging_embed(
            requester_display=requester_display,
            helper_displays=helper_displays,
            closer_display="System (Auto-cancelled)",
            requester_before=0,
            requester_after=0,
            helper_changes={},
            requester_id=requester_id,
            bosses=data.get("bosses", []),
            username=data.get("username", "—"),
            max_claims=data.get("max_claims", 0),
            claimers=claimers,
            guild=guild,
            type=data.get("type", "unknown"),
            created_at=data.get("created_at"),
            cancelled=True,
            closer_id=self.bot.user.id,
            id=data.get("ticket_id", 0),
        )

        # Notify channel before deleting
        try:
            await channel.send(
                "🗑️ This ticket was automatically cancelled due to inactivity (5 hours)."
            )
        except Exception:
            pass

        # ✅ Update Firestore properly
        ticket.reference.update(
            {
                "status": "cancelled",  # NOT closed
                "auto_closed": True,
                "closed_by": self.bot.user.id,
                "closed_at": firestore.SERVER_TIMESTAMP,
            }
        )

        # ✅ Log event
        await log_ticket_event(self.bot, embed=embed)

        # ✅ Update dashboard
        await update_dashboard(self.bot)

        # Delete channel
        try:
            await channel.delete()
        except Exception:
            pass
