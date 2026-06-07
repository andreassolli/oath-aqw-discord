import bisect
import random

import discord
from firebase_admin import firestore

from config import (
    ADMIN_ROLE_ID,
    GUIDE_CHANNEL_ID,
    HELPER_ROLE_ID,
    OATHSWORN_ROLE_ID,
    TICKET_CATEGORY_ID,
    TICKET_MESSAGES_CHANNEL_ID,
    TICKET_OFFICER_ROLE_ID,
    percentage_points,
    spam_points,
)
from firebase_client import db
from ticket_help.new_panel.log_panel import LogLayout
from ticket_help.new_panel.ticket_panel import TicketLayout
from ticket_help.panels.server_fetch import fetch_servers
from ticket_help.tickets.boss_type import get_bosses_for_type
from ticket_help.tickets.ids import get_next_ticket_id
from ticket_help.tickets.points import calculate_ticket_points, get_boss_room
from ticket_help.tickets.ticket_cache import ticket_cache
from ticket_help.tickets.utils import (
    find_guide_threads,
    set_active_ticket,
)
from ticket_help.utils.message_logging import log_ticket_view_event
from ticket_help.utils.ticket import get_overwrites

CORRECT_BOSS_ORDER = [
    "Ultra Dage",
    "Ultra Nulgath",
    "Ultra Drago",
    "Ultra Darkon",
    "Champion Drakath",
    "Ultra Speaker",
    "Ultra Gramiel",
]

TYPE_TO_IMAGE = {
    "weekly bosses": "https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/weeklyticket.png",
    "daily bosses": "https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/dailyticket.png",
    "7 man bosses": "https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/7manticket.png",
    "spamming": "https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/spamticket.png",
    "until drop": "https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/spamticket.png",
    "practice": "https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/practiceticket.png",
    "infinity": "https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/aqwi.png",
}

BOSS_ORDER_MAP = {boss: i for i, boss in enumerate(CORRECT_BOSS_ORDER)}


def sort_bosses(bosses: list[str]) -> list[str]:
    return sorted(bosses, key=lambda b: BOSS_ORDER_MAP.get(b, len(BOSS_ORDER_MAP)))


class CreateTicketModal(discord.ui.Modal):
    def __init__(
        self,
        ticket_type: str,
        username: str,
        servers,
        is_practice: bool = False,
        is_infinity: bool = False,
    ):
        super().__init__(title=f"Create {ticket_type.capitalize()} Ticket")

        self.type = ticket_type
        self.is_practice = is_practice
        self.is_infinity = is_infinity

        self.bosses_input: discord.ui.TextInput | None = None
        username = username if username else ""
        self.username = discord.ui.TextInput(label="Username", required=True)
        self.username.default = username
        self.add_item(self.username)

        if self.is_infinity:
            server_options = [
                discord.SelectOption(
                    label="Alpha 1",
                    value="Alpha 1",
                    description="Kaira's Server",
                ),
                discord.SelectOption(
                    label="Alpha 2",
                    value="Alpha 2",
                    description="Secundus' Server",
                ),
                discord.SelectOption(
                    label="Alpha 3",
                    value="Alpha 3",
                    description="Waldo's Server",
                ),
            ]
        else:
            server_options = [
                discord.SelectOption(
                    label=server["sName"],
                    value=server["sName"],
                    description=f"{server['iCount']}/{server['iMax']} players",
                )
                for server in servers
            ]
        self.server_select = discord.ui.Label(
            text="Server",
            component=discord.ui.Select(
                options=server_options,
                required=True,
            ),
        )
        self.add_item(self.server_select)
        # if self.type in {"other bosses", "spamming", "testing"}:
        #    self.room_input = discord.ui.TextInput(
        #        label="Room",
        #        placeholder="Private rooms need 4+ digits",
        #        required=True
        #    )
        #    self.add_item(self.room_input)
        #    self.room = None
        # else:

        if self.type in {
            "other bosses",
            "spamming",
            "testing",
            "until drop",
        }:
            self.bosses_input = discord.ui.TextInput(
                label="List boss rooms (comma-separated)",
                placeholder="Ectocave,WorldEnder,Voidlair...",
                required=True,
            )
            self.add_item(self.bosses_input)

        self.room = random.randint(11111, 99999)
        self.room_input = None
        self.server = ""

        if self.type in {
            "other bosses",
            "spamming",
            "testing",
            "until drop",
        }:
            self.max_claims_input = discord.ui.TextInput(
                label="Maximum helpers",
                placeholder="Digit between 1 and 20",
                required=True,
            )
            self.add_item(self.max_claims_input)
        else:
            self.max_claims_input = None
            self.max_claims = None

        if self.type == "until drop":
            self.total_drops_input = discord.ui.TextInput(
                label="Drop Rate % (comma-separated)",
                placeholder="1,2,5...",
                required=True,
            )
            self.add_item(self.total_drops_input)
        else:
            self.total_drops_input = None
            self.total_drops = None

        if self.type == "spamming":
            self.total_kills_input = discord.ui.TextInput(
                label="Total kills/runs",
                placeholder="Digit between 1 and 500",
                required=True,
            )
            self.add_item(self.total_kills_input)
        else:
            self.total_kills_input = None
            self.total_kills = 1
        if self.type in ["weekly bosses", "daily bosses", "7 man bosses"]:
            boss_options = get_bosses_for_type(self.type)
            options = []
            for boss in boss_options:
                option = discord.CheckboxGroupOption(
                    label=boss.get("name"),
                    value=boss.get("name"),
                )
                options.append(option)

            self.boss_selection = discord.ui.Label(
                text="Select the bosses for this ticket",
                component=discord.ui.CheckboxGroup(
                    options=options,
                    required=True,
                ),
            )
            self.add_item(self.boss_selection)
        if self.type == "weekly bosses":
            self.experienced_only = discord.ui.Label(
                text="Certificate only",
                component=discord.ui.CheckboxGroup(
                    options=[discord.CheckboxGroupOption(label="Enable", default=True)],
                    required=False,
                ),
            )
            self.add_item(self.experienced_only)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            try:
                room_value = (
                    int(self.room_input.value) if self.room_input else self.room
                )
            except ValueError:
                await interaction.followup.send(
                    "❌ Room must be a number.", ephemeral=True
                )
                return
            self.server = self.server_select.component.values[0]
            drops_list = []
            if self.type in {"weekly bosses", "daily bosses", "7 man bosses"}:
                bosses = sort_bosses(self.boss_selection.component.values)
            else:
                bosses = [
                    boss.strip()
                    for boss in self.bosses_input.value.split(",")
                    if boss.strip()
                ]

            if self.total_drops_input:
                drops_list = self.total_drops_input.value.strip().split(",")

            if self.total_kills_input:
                try:
                    total_kills_value = int(self.total_kills_input.value)
                except ValueError:
                    return await interaction.followup.send(
                        "❌ Total kills must be a number.", ephemeral=True
                    )
            else:
                total_kills_value = 1

            six_helper_bosses = [
                "Astral Shrine",
                "Grim Challenge",
                "Apex Azalith",
                "The Beast",
                "Void Trio",
                "Lich King",
                "Deimos",
                "Azalith",
                "Kathool Depths",
            ]

            if self.max_claims_input:
                try:
                    max_claims_value = int(self.max_claims_input.value)
                    if not 1 <= max_claims_value <= 20:
                        raise ValueError
                except ValueError:
                    return await interaction.followup.send(
                        "❌ Maximum helpers must be a number between **1 and 20**.",
                        ephemeral=True,
                    )
            elif self.type == "7 man bosses":
                max_claims_value = 6
            else:
                max_claims_value = 3

            points = 0
            if self.is_practice:
                for boss in bosses:
                    points += 1

            elif self.type in {"other bosses", "spamming", "testing"}:
                if self.type == "spamming":
                    selected_spam = bosses[0]
                    if selected_spam == "All TempleShrine":
                        points = int(total_kills_value * 1.75)
                    elif selected_spam == "Middle TempleShrine":
                        points = int(total_kills_value * 0.75)
                    elif selected_spam in [
                        "Right TempleShrine",
                        "Left TempleShrine",
                    ]:
                        points = int(total_kills_value * 0.5)
                    elif selected_spam == "Flame Usurper":
                        points = int(total_kills_value * 0.4)
                        max_claims_value = 1
                    else:
                        bosses = [
                            boss.strip() for boss in self.bosses_input.value.split(",")
                        ]
                        index = bisect.bisect_left(spam_points, total_kills_value)
                        points = index if index > 0 else 1
            elif self.type == "until drop":
                bosses = [boss.strip() for boss in self.bosses_input.value.split(",")]

                drop_rates = []
                for drops in self.total_drops_input.value.split(","):
                    drops = drops.strip().replace("%", "")  # allow "5%" or "5"

                    if not drops.isdigit():
                        return await interaction.followup.send(
                            "❌ Drop rates must be numbers like `1,2,5` (no text).",
                            ephemeral=True,
                        )

                    drop_rates.append(percentage_points.get(int(drops), 1))

                points = min(sum(drop_rates), 12)
            else:
                points = 0
                for boss in bosses:
                    points += calculate_ticket_points(boss)

            ticket_id = get_next_ticket_id()
            channel_name = f"「🔖」ticket-{ticket_id:03d}"
            ticket_name = f"ticket-{ticket_id:03d}"
            category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
            experienced_only = False
            if (
                self.type == "weekly bosses"
                and len(self.experienced_only.component.values) > 0
            ):
                experienced_only = self.experienced_only.component.values[0]

            overwrites = get_overwrites(interaction)
            channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
            )

            log_layout = LogLayout(
                requester_id=interaction.user.id,
                bosses=bosses,
                points=points,
                username=self.username.value,
                room=str(room_value),
                max_claims=max_claims_value,
                claimers=[],
                guild=interaction.guild,
                type=self.type,
                server=self.server,
                total_kills=str(total_kills_value),
                drops=drops_list,
                ticket_name=ticket_name,
                claimer_roles={str(interaction.user.id): "DPS"},
                certificate_only=experienced_only,
                is_practice=self.is_practice,
            )

            embed = discord.Embed(
                color=discord.Colour(7344907),
            )

            if self.is_practice:
                embed.set_image(url=TYPE_TO_IMAGE["practice"])
            elif self.is_infinity:
                embed.set_image(url=TYPE_TO_IMAGE["infinity"])
            else:
                embed.set_image(url=TYPE_TO_IMAGE[self.type])

            await channel.send(embed=embed)
            thread_channel = interaction.guild.get_channel(TICKET_MESSAGES_CHANNEL_ID)
            thread_obj = await thread_channel.create_thread(
                name=ticket_name,
                embed=embed,
            )

            thread = thread_obj.thread
            await log_ticket_view_event(interaction.client, thread.id, view=log_layout)
            ticket_cache[channel.id] = {
                "ticket_name": ticket_name,
                "thread_id": thread.id,
            }
            db.collection("tickets").document(ticket_name).set(
                {
                    "ticket_id": ticket_id,
                    "channel_id": channel.id,
                    "thread_id": thread.id,
                    "user_id": interaction.user.id,
                    "bosses": bosses,
                    "points": points,
                    "drops": drops_list,
                    "max_claims": max_claims_value,
                    "claimers": [],
                    "username": self.username.value,
                    "room": room_value,
                    "status": "open",
                    "type": self.type,
                    "server": self.server,
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "reping_helpers": True,
                    "reminder_sent": False,
                    "auto_closed": False,
                    "total_kills": total_kills_value,
                    "experienced_only": experienced_only,
                    "claimer_roles": {str(interaction.user.id): "DPS"},
                    "is_practice": self.is_practice,
                }
            )

            layout = TicketLayout(
                requester_id=interaction.user.id,
                bosses=bosses,
                points=points,
                username=self.username.value,
                room=str(room_value),
                max_claims=max_claims_value,
                claimers=[],
                guild=interaction.guild,
                type=self.type,
                server=self.server,
                total_kills=str(total_kills_value),
                drops=drops_list,
                ticket_name=ticket_name,
                claimer_roles={str(interaction.user.id): "DPS"},
                certificate_only=experienced_only,
                is_practice=self.is_practice,
            )

            allowed_mentioning = discord.AllowedMentions(
                users=True, roles=True, everyone=False
            )

            message = await channel.send(
                view=layout,
                allowed_mentions=allowed_mentioning,
            )

            guide_threads = await find_guide_threads(
                guild=interaction.guild,
                guide_channel_id=GUIDE_CHANNEL_ID,
                bosses=bosses,
            )

            if guide_threads:
                lines = []
                for boss, thread in guide_threads.items():
                    lines.append(f"• **{boss}** → [{thread.name}]({thread.jump_url})")
                embed = discord.Embed(
                    title="📘 **Relevant Guides**",
                    description="\n".join(lines),
                    color=discord.Colour(7344907),
                )

                await channel.send(embed=embed)

            helper_role = interaction.guild.get_role(HELPER_ROLE_ID)

            await channel.send(
                f"{helper_role.mention}\n⚠️ **More helpers needed for this ticket!**",
                allowed_mentions=discord.AllowedMentions(roles=True),
            )

            db.collection("tickets").document(ticket_name).update(
                {
                    "message_id": message.id,
                    "last_helper_ping": firestore.SERVER_TIMESTAMP,
                }
            )

            set_active_ticket(interaction.user.id, ticket_name)
            await interaction.followup.send(
                f"✅ Ticket created: {channel.mention}", ephemeral=True
            )
            lines = []

            for boss in bosses:
                custom_tickets = {"spamming", "testing", "until drop"}
                if self.type in custom_tickets:
                    if "TempleShrine" in boss:
                        rooms = "templeshrine"
                    elif "Flame Usurper" in boss:
                        rooms = "flameusurper"
                    else:
                        rooms = boss
                else:
                    rooms = get_boss_room(boss)

                if not rooms:
                    continue

                # Split multiple rooms by comma
                room_list = [r.strip() for r in rooms.split(",")]

                for room in room_list:
                    lines.append(f"```/join {room}-{layout.room}```")

            rooms_text = "".join(lines)

            await interaction.followup.send(
                f"📋 **Room codes:**\n{rooms_text}", ephemeral=True
            )

            try:
                await message.pin(reason="Ticket information")
            except discord.Forbidden:
                # Bot is missing 'Manage Messages'
                pass

        except Exception as e:
            await interaction.followup.send(
                "❌ Something went wrong while creating the ticket. Please check your inputs.",
                ephemeral=True,
            )
            raise e
