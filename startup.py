from class_setups.utils import build_class_index
from ticket_help.panels.restore_tickets import restore_tickets
from user_verification.restore_join_tickets import restore_join_tickets


async def run_startup_tasks(bot):
    await build_class_index()
    await restore_tickets(bot)
    await restore_join_tickets(bot)
