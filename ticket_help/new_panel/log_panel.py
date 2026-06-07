import discord

from firebase_client import db

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


def format_points(points: int) -> str:
    digits = str(points)

    return "".join(POINTS_MAP[int(digit)] for digit in digits)


class LogLayout(discord.ui.LayoutView):
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
        completed_bosses: list[str] = [],
        claimer_roles: dict[str, str] | None = None,
        notes: str | None = None,
        certificate_only: bool = False,
        is_practice: bool = False,
    ):
        super().__init__(timeout=None)

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
        self.completed_bosses = completed_bosses
        self.certificate_only = certificate_only
        self.is_practice = is_practice

        boss_list = [boss for boss in bosses if boss not in completed_bosses]
        self.boss_list = boss_list
        requester_member = guild.get_member(requester_id)
        requester_mention = (
            requester_member.mention if requester_member else f"<@{requester_id}>"
        )

        boss_string = ""
        x = 0
        for boss in boss_list:
            boss_string += f"{boss}, "
            x += 1
            if x % 3 == 0:
                boss_string += "\n"

        for boss in completed_bosses:
            boss_string += f"~~{boss}~~, "
            x += 1
            if x % 3 == 0:
                boss_string += "\n"

        boss_string = boss_string.rstrip(", \n")
        if int(total_kills) > 1:
            boss_string += f" ({total_kills} kills)"

        items: list[discord.ui.Item] = []
        if type == "weekly bosses":
            items.append(
                discord.ui.TextDisplay(
                    content=f"<:medal:1505158451179819119> **Points:** \n>    {format_points(points)}"
                )
            )
        else:
            items.append(
                discord.ui.TextDisplay(
                    content=f"<:medal:1505158451179819119> **Points:** \n>    {format_points(points)}"
                ),
            )
        items.extend(
            [
                discord.ui.Separator(
                    visible=False,
                    spacing=discord.SeparatorSpacing.small,
                ),
                discord.ui.TextDisplay(
                    content=f"<:id2:1505158104810262558> **Requester** {requester_mention} ({username}){'\n >>> ' + notes if notes else ''}"
                ),
                discord.ui.TextDisplay(content=f"Selected server: \n> **{server}**"),
            ]
        )

        items.append(discord.ui.TextDisplay(content=f"Bosses: \n>>> {boss_string}"))

        items.extend(
            [
                discord.ui.Separator(
                    visible=True,
                    spacing=discord.SeparatorSpacing.large,
                ),
            ]
        )

        self.container = discord.ui.Container(
            *items,
            accent_colour=discord.Colour(7344907),
        )

        self.add_item(self.container)

    @property
    def doc_ref(self):
        return db.collection("tickets").document(self.ticket_name)

    def get_ticket_data(self):
        doc = self.doc_ref.get()

        if not doc.exists:
            return None

        return doc.to_dict()
