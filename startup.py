from class_setups.utils import build_class_index
from tasks import setup_tasks
from ticket_help.panels.restore_tickets import restore_tickets
from user_verification.restore_join_tickets import restore_join_tickets
from utils import unlock_all_coins


async def run_startup_tasks(bot):
    await unlock_all_coins()
    await build_class_index()
    await restore_tickets(bot)
    await restore_join_tickets(bot)
    setup_tasks(bot)
