from ticket_help.new_panel.ticket_panel import TicketLayout


async def refresh_ticket_message(
    interaction,
    ticket_data,
    ticket_name,
):
    message_id = ticket_data.get("message_id")

    if not message_id:
        return

    message = await interaction.channel.fetch_message(message_id)

    layout = TicketLayout(
        requester_id=ticket_data["user_id"],
        ticket_name=ticket_name,
        bosses=ticket_data["bosses"],
        points=ticket_data["points"],
        username=ticket_data["username"],
        room=ticket_data["room"],
        max_claims=ticket_data["max_claims"],
        claimers=ticket_data["claimers"],
        guild=interaction.guild,
        type=ticket_data["type"],
        server=ticket_data["server"],
        total_kills=ticket_data.get("total_kills", "0"),
        claimer_roles=ticket_data.get("claimer_roles", {}),
    )

    await message.edit(view=layout)
