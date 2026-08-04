async def refresh_ticket_panel(client):
    from panels.create_ticket_panel import setup_new_tickets
    await setup_new_tickets(client)
