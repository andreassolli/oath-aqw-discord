"""
ticket_help package

This module exposes setup helpers for the ticket system.
It does NOT create or run a Discord client.
"""

from quests.setup_quests import setup_quests
from ticket_help.panels.update_ticket_counter import update_ticket

from .dashboard.updater import update_dashboard
from .panels.panel_setup import setup_ticket_panel
from .tickets.auto_manager import TicketAutoManager


async def setup_ticket_system(bot):
    """
    Called once when the bot is ready.
    Starts background ticket systems and panels.
    """
    TicketAutoManager(bot)
    await setup_ticket_panel(bot)
    await update_dashboard(bot)
    await update_ticket(bot)
    await setup_quests(bot)
