from datetime import datetime, timedelta

import discord
from firebase_admin import firestore

from config import (
    DAGE_CERTIFICATE_ID,
    DARKON_CERTIFICATE_ID,
    DRAGO_CERTIFICATE_ID,
    DRAKATH_CERTIFICATE_ID,
    EXPERIENCED_HELPER_ROLE_ID,
    GRAMIEL_CERTIFICATE_ID,
    HELPER_ROLE_ID,
    NULGATH_CERTIFICATE_ID,
    SPEAKER_CERTIFICATE_ID,
)
from firebase_client import db
from ticket_help.commands.permissions import (
    has_admin_role,
    has_oathsworn_role,
)
from ticket_help.modals.boss_modal import ChangeBossModal
from ticket_help.modals.cancel_modal import CancelModal
from ticket_help.modals.confirm_modal import ConfirmModal
from ticket_help.modals.role_modal import RoleModal
from ticket_help.modals.server_modal import ServerModal
from ticket_help.panels.server_fetch import fetch_servers
from ticket_help.tickets.boss_type import get_bosses_for_type
from ticket_help.tickets.points import get_boss_room
from ticket_help.tickets.utils import clear_active_ticket, set_active_ticket

POINTS_MAP = {
    0: "<:0w:1505157488008499351>",
    9: "<:9w:1505157489006612640>",
    8: "<:8w:1505157486632763423>",
    7: "<:7w:1505157484833407076>",
    6: "<:6w:1505157490831265903>",
    5: "<:5w:1505157496531058759>",
    4: "<:4w:1505157498569621534>",
    3: "<:3w:1505157500197015723>",
    2: "<:2w:1505157501367226518>",
    1: "<:1w:1505157502428381225>",
}

BOSS_TO_CERTIFICATE = {
    "Champion Drakath": DRAKATH_CERTIFICATE_ID,
    "Ultra Dage": DAGE_CERTIFICATE_ID,
    "Ultra Drago": DRAGO_CERTIFICATE_ID,
    "Ultra Darkon": DARKON_CERTIFICATE_ID,
    "Ultra Speaker": SPEAKER_CERTIFICATE_ID,
    "Ultra Gramiel": GRAMIEL_CERTIFICATE_ID,
    "Ultra Nulgath": NULGATH_CERTIFICATE_ID,
}


def format_points(points: int) -> str:
    digits = str(points)

    return "".join(POINTS_MAP[int(digit)] for digit in digits)


class TicketLayout(discord.ui.LayoutView):
    def __init__(
        self,
        requester_id: int,
        ticket_name: str,
        bosses: list[str],
        points: int,
        username: str,
        room: str,
        max_claims: int,
        claimers: list[int],
        guild: discord.Guild,
        type: str,
        server: str,
        total_kills: str,
        drops: list[str] = [],
        claimer_roles: dict[str, str] | None = None,
        notes: str | None = None,
    ):
        super().__init__()

        self.requester_id = requester_id
        self.bosses = bosses
        self.points = points
        self.username = username
        self.room = room
        self.max_claims = max_claims
        self.claimers = claimers
        self.guild = guild
        self.type = type
        self.server = server
        self.total_kills = total_kills
        self.drops = drops
        self.claimer_roles = claimer_roles or {}
        self.notes = notes
        self.ticket_name = ticket_name

        self.container1 = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"<:medal:1505158451179819119> **Points:** \n>    {format_points(points)}"
            ),
            discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"<:id2:1505158104810262558> **Requester** <@{requester_id}> ({username}){'\n >>> ' + notes if notes else ''}"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"Selected server: \n> **{server}**"),
                accessory=ChangeButton(),
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"Bosses: \n>>> {', '.join(bosses)}"),
                accessory=BossButton(),
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content="Still in need of help? **Ping helpers!**"
                ),
                accessory=PingButton(),
            ),
            discord.ui.TextDisplay(content="Finished with the ticket?"),
            discord.ui.ActionRow(
                CompleteButton(),
                CancelButton(),
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"<:hands:1505158458494681138> **Helpers** ({len(claimers)}/{max_claims})\n- {', '.join([f'<@{helper}>' for helper in claimers])}"
                ),
                accessory=RoleButton(),
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content="Forgot room codes? Click **Room codes**!"
                ),
                accessory=RoomButton(),
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(content="Claim the ticket, and get room codes!"),
                accessory=ClaimButton(),
            ),
            accent_colour=discord.Colour(7344907),
        )

        self.add_item(self.container1)

    def is_admin(self, interaction):
        return has_admin_role(interaction)

    def is_requester(self, interaction):
        return interaction.user.id == self.requester_id

    def can_manage_ticket(self, interaction):
        return (
            self.is_requester(interaction)
            or has_admin_role(interaction)
            or has_oathsworn_role(interaction)
        )

    @property
    def doc_ref(self):
        return db.collection("tickets").document(self.ticket_name)

    def get_ticket_data(self):
        doc = self.doc_ref.get()

        if not doc.exists:
            return None

        return doc.to_dict()


class ChangeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Change server",
            style=discord.ButtonStyle.secondary,
            emoji=discord.PartialEmoji(
                name="server_change",
                id=1503809700515282984,
            ),
            custom_id="change_server_button",
        )

    async def callback(self, interaction: discord.Interaction):
        layout: TicketLayout = self.view

        if not layout.can_manage_ticket(interaction):
            return await interaction.response.send_message(
                "🚫 Only the ticket creator or admin can do this.",
                ephemeral=True,
            )

        servers = await fetch_servers()

        await interaction.response.send_modal(
            ServerModal(servers, current=layout.server)
        )


class RoomButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Room codes",
            style=discord.ButtonStyle.secondary,
            emoji=discord.PartialEmoji(
                name="clips",
                id=1505158447845609593,
            ),
            custom_id="room_code_button",
        )

    async def callback(self, interaction: discord.Interaction):
        layout: TicketLayout = self.view
        data = layout.get_ticket_data()
        claimers = data.get("claimers", [])

        requester_id = data.get("user_id")
        if interaction.user.id not in claimers and interaction.user.id != requester_id:
            return await interaction.response.send_message(
                "❌ You must claim this ticket first!", ephemeral=True
            )

        lines = []

        for boss in layout.bosses:
            custom_tickets = {"spamming", "testing", "until drop"}
            if data.get("type") in custom_tickets:
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

        await interaction.response.send_message(
            f"📋 **Room codes:**\n{rooms_text}", ephemeral=True
        )


class RoleButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Change role",
            style=discord.ButtonStyle.secondary,
            emoji=discord.PartialEmoji(
                name="change_role",
                id=1505157332630376498,
            ),
            custom_id="role_button",
        )

    async def callback(self, interaction: discord.Interaction):
        layout: TicketLayout = self.view
        data = layout.get_ticket_data()
        if not data:
            return await interaction.response.send_message(
                "❌ Ticket data not found.",
                ephemeral=True,
            )

        requester = data.get("user_id")
        claimers = data.get("claimers", [])
        claimer_roles = data.get("claimer_roles", {})
        user_id = interaction.user.id
        if user_id not in claimers and user_id != requester:
            return await interaction.response.send_message(
                "❌ Only claimers and requester can change roles.",
                ephemeral=True,
            )

        await interaction.response.send_modal(
            RoleModal(
                roles=claimer_roles,
                boss="Speaker" if data.get("type") == "weekly bosses" else "Grim",
            )
        )


class ClaimButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Claim ticket",
            style=discord.ButtonStyle.success,
            emoji=discord.PartialEmoji(
                name="claiming",
                id=1505158455412002846,
            ),
            custom_id="claim_ticket_button",
        )

    async def callback(self, interaction: discord.Interaction):
        layout: TicketLayout = self.view

        data = layout.get_ticket_data()

        if not data:
            return await interaction.response.send_message(
                "❌ Ticket data not found.",
                ephemeral=True,
            )
        claimers = data.get("claimers", [])

        requester_id = data.get("user_id")
        is_requester = interaction.user.id == requester_id
        if interaction.user.id in claimers:
            claimers.remove(interaction.user.id)

            roles = data.get("claimer_roles", {})

            roles.pop(str(interaction.user.id), None)

            layout.doc_ref.update(
                {
                    "claimers": claimers,
                    "claimer_roles": roles,
                }
            )

            clear_active_ticket(interaction.user.id, layout.ticket_name)

            await self._update_ticket_embed(interaction)

            await interaction.channel.send(
                f"🔁 {interaction.user.mention} unclaimed this ticket "
                f"({len(claimers) + 1}/{layout.max_claims + 1})"
            )
            return

        if len(claimers) >= layout.max_claims:
            return await interaction.followup.send(
                "🚫 No more spots available.", ephemeral=True
            )

        user_ref = db.collection("users").document(str(interaction.user.id))
        user_doc = user_ref.get()
        active_ticket = (
            user_doc.to_dict().get("active_ticket") if user_doc.exists else None
        )
        if user_doc.exists and active_ticket and active_ticket != layout.ticket_name:
            return await interaction.followup.send(
                "🚫 You are already helping on another ticket.", ephemeral=True
            )

        if is_requester:
            return await interaction.followup.send(
                "🚫 Ticket creator cannot claim their own ticket.",
                ephemeral=True,
            )

        experienced_only = data.get("experienced_only", False)

        member = interaction.user
        guild = interaction.guild

        helper_role = guild.get_role(HELPER_ROLE_ID)
        bot_guy_role = guild.get_role(BOT_GUY_ROLE_ID)

        has_helper = helper_role in member.roles if helper_role else False
        has_bot_guy = bot_guy_role in member.roles if bot_guy_role else False

        needed_certificates = []
        for boss in layout.bosses:
            if boss in BOSS_TO_CERTIFICATE:
                needed_certificates.append(BOSS_TO_CERTIFICATE[boss])

        member_role_ids = {role.id for role in member.roles}

        if experienced_only:
            for cert in needed_certificates:
                if not is_requester and cert not in member_role_ids:
                    return await interaction.followup.send(
                        "🚫 You need a **Certification** for one or more of the bosses in this ticket.",
                        ephemeral=True,
                    )
        else:
            if not has_helper and not has_bot_guy:
                return await interaction.followup.send(
                    "🚫 You must be a helper to claim this ticket.",
                    ephemeral=True,
                )
        if "Grim Challenge" in layout.bosses or "Ultra Speaker" in layout.bosses:
            roles = data.get("claimer_roles", {})
            return await interaction.followup.send_modal(
                RoleModal(
                    roles=roles,
                    boss="Speaker" if layout.type == "weekly bosses" else "Grim",
                )
            )

        claimers.append(interaction.user.id)
        layout.doc_ref.update({"claimers": claimers})
        set_active_ticket(interaction.user.id, layout.ticket_name)


class PingButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Ping helpers",
            style=discord.ButtonStyle.secondary,
            emoji=discord.PartialEmoji(
                name="notifi",
                id=1505158449414013008,
            ),
            custom_id="ping_helpers_button",
        )

    async def callback(self, interaction: discord.Interaction):
        layout: TicketLayout = self.view

        if not layout.can_manage_ticket(interaction):
            return await interaction.response.send_message(
                "🚫 Only the ticket creator or admin can do this.",
                ephemeral=True,
            )

        data = layout.get_ticket_data()

        if not data:
            return await interaction.response.send_message(
                "❌ Ticket data not found.",
                ephemeral=True,
            )

        now = datetime.utcnow()
        last_ping = data.get("last_helper_ping")

        if last_ping:
            last_ping_dt = last_ping.replace(tzinfo=None)
            remaining = timedelta(minutes=10) - (now - last_ping_dt)

            if remaining.total_seconds() > 0:
                mins, secs = divmod(int(remaining.total_seconds()), 60)
                return await interaction.response.send_message(
                    f"⏳ Helpers were pinged recently.\n"
                    f"Try again in **{mins}m {secs}s**.",
                    ephemeral=True,
                )

        helper_role = interaction.guild.get_role(HELPER_ROLE_ID)

        if not helper_role:
            return await interaction.response.send_message(
                "❌ Helper role not found.", ephemeral=True
            )

        layout.doc_ref.update({"last_helper_ping": firestore.SERVER_TIMESTAMP})

        await interaction.response.send_message(
            "📣 Helpers have been pinged!", ephemeral=True
        )

        await interaction.channel.send(
            f"{helper_role.mention}\n⚠️ **More helpers needed for this ticket!**",
            allowed_mentions=discord.AllowedMentions(roles=True),
        )


class BossButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Change bosses",
            style=discord.ButtonStyle.secondary,
            emoji=discord.PartialEmoji(
                name="chuckless",
                id=1505158446084001884,
            ),
            custom_id="change_bosses_button",
        )

    async def callback(self, interaction: discord.Interaction):
        layout: TicketLayout = self.view
        if not layout.can_manage_ticket(interaction):
            return await interaction.response.send_message(
                "🚫 Only the ticket creator or admin can do this.",
                ephemeral=True,
            )

        ticket_data = layout.get_ticket_data()
        if not ticket_data:
            return await interaction.response.send_message(
                "❌ Ticket data not found.",
                ephemeral=True,
            )

        bosses = ticket_data.get("bosses", [])
        ticket_type = ticket_data.get("type", "weekly bosses")

        await interaction.response.send_modal(
            ChangeBossModal(
                bosses=get_bosses_for_type(ticket_type),
                current=bosses,
            )
        )


class CompleteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Complete ticket",
            style=discord.ButtonStyle.success,
            emoji=discord.PartialEmoji(
                name="complete_ticket",
                id=1505157129252634706,
            ),
            custom_id="complete_ticket_button",
        )

    async def callback(self, interaction: discord.Interaction):
        layout: TicketLayout = self.view
        if not layout.can_manage_ticket(interaction):
            return await interaction.response.send_message(
                "🚫 Only the ticket creator or an admin can cancel this ticket.",
                ephemeral=True,
            )
        data = layout.get_ticket_data()
        if not data:
            return await interaction.response.send_message(
                "❌ Ticket data not found.",
                ephemeral=True,
            )
        bosses = data.get("bosses", [])
        await interaction.response.send_modal(ConfirmModal(bosses=bosses))


class CancelButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Cancel ticket",
            style=discord.ButtonStyle.danger,
            emoji=discord.PartialEmoji(
                name="cancel_ticket",
                id=1505157128069976284,
            ),
            custom_id="cancel_ticket_button",
        )

    async def callback(self, interaction: discord.Interaction):
        layout: TicketLayout = self.view
        if not layout.can_manage_ticket(interaction):
            return await interaction.response.send_message(
                "🚫 Only the ticket creator or an admin can cancel this ticket.",
                ephemeral=True,
            )

        await interaction.response.send_modal(CancelModal())
