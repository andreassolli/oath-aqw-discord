import discord

from firebase_client import db
from ticket_help.tickets.embed_utils import build_ticket_embed
from ticket_help.tickets.views import TicketActionView


async def restore_tickets(bot: discord.Client):
    tickets = (
        db.collection("tickets").where("status", "in", ["open", "claimed"]).stream()
    )

    for doc in tickets:
        data = doc.to_dict()
        if not data:
            continue

        channel_id = data.get("channel_id")
        message_id = data.get("message_id")

        if not channel_id or not message_id:
            continue

        channel = bot.get_channel(channel_id)
        if not channel:
            continue

        try:
            message = await channel.fetch_message(message_id)
        except:
            continue

        # 🔥 Rebuild embed from DB state
        embed = build_ticket_embed(
            requester_id=data["user_id"],
            bosses=data["bosses"],
            points=data["points"],
            username=data["username"],
            room=str(data["room"]),
            max_claims=data["max_claims"],
            claimers=data.get("claimers", []),
            guild=channel.guild,
            type=data["type"],
            server=data["server"],
            total_kills=str(data.get("total_kills", 1)),
        )

        # 🔥 Rebuild view from DB state
        view = TicketActionView(
            ticket_name=doc.id,
            max_claims=data["max_claims"],
            room=str(data["room"]),
            bosses=data["bosses"],
        )

        await message.edit(embed=embed, view=view)
