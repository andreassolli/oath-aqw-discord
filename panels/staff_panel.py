import discord

from config import (
    GRAND_OATHSWORN_ROLE_ID,
    KJ_ROLE_ID,
    OATHKEEPER_ROLE_ID,
    OATHSWORN_ROLE_ID,
)

LEADER = [
    {
        "name": "King Johnson (Away)",
        "discord": 993034909021126667,
        "description": "",
        "image": "kingjohnsonpfp",
    },
]

CO_LEADS = [
    {
        "name": "Bionicle",
        "discord": 315691280472473601,
        "description": "",
        "image": "bioniclepfp",
    },
    {
        "name": "Cohl",
        "discord": 1456871413985181822,
        "description": "Mascot",
        "image": "cohlpfp",
    },
    {
        "name": "Double Dee",
        "discord": 930861700457054359,
        "description": "",
        "image": "doubledeepfp",
    },
    {
        "name": "Proxy",
        "discord": 292040660696039424,
        "description": "",
        "image": "proxypfp",
    },
    {
        "name": "Xsosxquickiller",
        "discord": 463869761625915393,
        "description": "",
        "image": "killerpfp",
    },
]

HEAD_OFFICERS = [
    {
        "name": "StarGirl",
        "discord": 1255360134708858984,
        "description": "",
        "image": "stargirlpfp",
    },
]

OFFICERS = [
    {
        "name": "Big Rig",
        "discord": 551064861707206677,
        "description": "",
        "image": "bigrigpfp",
    },
    {
        "name": "Fird",
        "discord": 782789672870215680,
        "description": "",
        "image": "firdpfp",
    },
    {
        "name": "Greed",
        "discord": 1019047129882300486,
        "description": "",
        "image": "greedpfp",
    },
    {
        "name": "Iucy",
        "discord": 1433079662891761744,
        "description": "",
        "image": "lucypfp",
    },
    {
        "name": "Krydoom",
        "discord": 281325339307933696,
        "description": "",
        "image": "krydoompfp",
    },
    {
        "name": "Maou",
        "discord": 692949538306260992,
        "description": "",
        "image": "maoupfp",
    },
    {
        "name": "OG San",
        "discord": 764704496784769024,
        "description": "",
        "image": "ogsanpfp",
    },
    {
        "name": "Smoked Out",
        "discord": 696254108788719627,
        "description": "",
        "image": "smokedoutpfp",
    },
    {"name": "TophaCouf", "discord": None, "description": "", "image": "tophpfp"},
]


PREVIOUS = [
    {
        "name": "Mapril",
        "discord": 345741637487689732,
        "description": "Ex Head-Officer, done more than we can add!",
        "image": "maprilpfp",
        "period": "Jan. '26 - Jun. '26",
    },
    {
        "name": "Samdal",
        "discord": 459983264224903168,
        "description": "Helped shape ticket system & certificates",
        "image": "samdalpfp",
        "period": "Mar. '26 - Jun. '26",
    },
    {
        "name": "Bet",
        "discord": None,
        "description": "Helped during the start of the Discord",
        "image": "betpfp",
        "period": "Jan. '26 - May. '26",
    },
]


class LeadLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__()

        components: list[discord.ui.Item] = [
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/oathstaff.png",
                ),
            ),
            discord.ui.TextDisplay(content=f"**Leader / <@{KJ_ROLE_ID}>**"),
        ]

        components.extend(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"{f'<@&{user['discord']}>' if discord is not None else user['name']}"
                ),
                accessory=discord.ui.Thumbnail(
                    media=f"https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/{user['image']}",
                ),
            )
            for user in LEADER
        )

        components.append(
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
        )

        components.append(
            discord.ui.TextDisplay(content=f"**Co-Leads / <@{OATHKEEPER_ROLE_ID}>**"),
        )

        components.extend(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"{f'<@&{user['discord']}>' if discord is not None else user['name']}"
                ),
                accessory=discord.ui.Thumbnail(
                    media=f"https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/{user['image']}",
                ),
            )
            for user in CO_LEADS
        )

        container = discord.ui.Container(
            *components, accent_colour=discord.Colour(7344907)
        )
        self.add_item(container)


class OfficerLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__()

        components: list[discord.ui.Item] = [
            discord.ui.TextDisplay(
                content=f"**Head Officers / <@{GRAND_OATHSWORN_ROLE_ID}>**"
            ),
        ]

        components.extend(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"{f'<@&{user['discord']}>' if discord is not None else user['name']}"
                ),
                accessory=discord.ui.Thumbnail(
                    media=f"https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/{user['image']}",
                ),
            )
            for user in HEAD_OFFICERS
        )

        components.append(
            discord.ui.TextDisplay(content=f"**Officers / <@{OATHSWORN_ROLE_ID}>**"),
        )

        components.extend(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"{f'<@&{user['discord']}>' if discord is not None else user['name']}"
                ),
                accessory=discord.ui.Thumbnail(
                    media=f"https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/{user['image']}",
                ),
            )
            for user in OFFICERS
        )

        components.append(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bright_separator.png",
                ),
            ),
        )
        container = discord.ui.Container(
            *components, accent_colour=discord.Colour(7344907)
        )
        self.add_item(container)


class ExLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__()

        components: list[discord.ui.Item] = [
            discord.ui.TextDisplay(content="**Past Officers**"),
        ]

        components.extend(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"{f'<@&{user['discord']}>' if discord is not None else user['name']} *{user['period']}*"
                ),
                accessory=discord.ui.Thumbnail(
                    media=f"https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/{user['image']}",
                ),
            )
            for user in PREVIOUS
        )

        container = discord.ui.Container(
            *components, accent_colour=discord.Colour(7344907)
        )
        self.add_item(container)


class EndLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__()

        components = [
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bright_separator.png",
                ),
            ),
        ]

        container = discord.ui.Container(
            *components, accent_colour=discord.Colour(7344907)
        )
        self.add_item(container)
