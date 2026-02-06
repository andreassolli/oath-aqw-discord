import discord
from discord.ext import tasks
from datetime import datetime, timedelta, timezone
from firebase_client import db

REMINDER_AFTER = timedelta(minutes=30)
AUTOCLOSE_AFTER = timedelta(hours=6)

class TicketAutoManager:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.ticket_watcher.start()

    def cog_unload(self):
        self.ticket_watcher.cancel()

    @tasks.loop(minutes=1)
    async def ticket_watcher(self):
        now = datetime.now(timezone.utc)

        tickets = db.collection("tickets") \
            .where("status", "==", "open") \
            .stream()

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
            if (
                age >= REMINDER_AFTER
                and not data.get("reminder_sent", False)
            ):
                try:
                    user = await self.bot.fetch_user(data["user_id"])

                    claimers = data.get("claimers", [])
                    max_claims = data.get("max_claims", 0)

                    messages = [
                        f"⏰ {user.mention} **Reminder:**",
                        "Please complete or close this ticket if it’s done."
                    ]

                    await channel.send("\n".join(messages))

                except Exception:
                    pass

                ticket.reference.update({
                    "reminder_sent": True
                })


            # 🔒 12-hour autoclose
            if age >= AUTOCLOSE_AFTER:
                await self.auto_close(ticket, data, channel)

    async def auto_close(self, ticket, data, channel):
        try:
            await channel.send(
                "🔒 This ticket has been automatically closed due to inactivity (12 hours)."
            )
        except Exception:
            pass

        ticket.reference.update({
            "status": "closed",
            "auto_closed": True,
            "closed_at": datetime.now(timezone.utc),
        })

        try:
            await channel.delete()
        except Exception:
            pass
