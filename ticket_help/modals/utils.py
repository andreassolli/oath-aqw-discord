from ticket_help.new_panel.ticket_panel import TicketLayout


def build_ticket_layout(ticket_data, guild):
    return TicketLayout(
        requester_id=ticket_data["user_id"],
        bosses=ticket_data["bosses"],
        points=ticket_data["points"],
        username=ticket_data["username"],
        room=ticket_data["room"],
        max_claims=ticket_data["max_claims"],
        claimers=ticket_data["claimers"],
        guild=guild,
        type=ticket_data["type"],
        server=ticket_data["server"],
        total_kills=ticket_data.get("total_kills", "0"),
        claimer_roles=ticket_data.get("claimer_roles", {}),
        ticket_name=ticket_data["ticket_name"],
    )
