import discord
from discord import app_commands
from config import TOKEN
from panels.panel_setup import setup_ticket_panel
from dashboard.updater import update_dashboard
from commands.admin import (
    reload_point_rules,
    set_boss_points,
    reset_all_points,
    set_user_points,
    add_boss,
    delete_boss,
    lookup_points,
    delete_type,
    add_points,
    subtract_points,
    remove_claimer,
    sync_usernames
)
from tickets.auto_manager import TicketAutoManager

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.add_command(reload_point_rules)
        self.tree.add_command(set_boss_points)
        self.tree.add_command(reset_all_points)
        self.tree.add_command(set_user_points)
        self.tree.add_command(add_boss)
        self.tree.add_command(delete_boss)
        self.tree.add_command(lookup_points)
        self.tree.add_command(delete_type)
        self.tree.add_command(add_points)
        self.tree.add_command(subtract_points)
        self.tree.add_command(remove_claimer)
        self.tree.add_command(sync_usernames)

        await self.tree.sync()


client = MyClient()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    TicketAutoManager(client)
    print("Ticket auto manager started")

    await setup_ticket_panel(client)
    await update_dashboard(client)



client.run(TOKEN)
