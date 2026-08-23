import json
import math
from pathlib import Path

import discord
from discord import app_commands

from extra_commands.preview_outfit import render_png


JSON_FILE = Path("bonus_packages_with_images.json")
PAGE_SIZE = 5


with JSON_FILE.open("r", encoding="utf-8") as f:
    BONUS_PACKAGES = json.load(f)


ITEM_ICONS = {
    "Axe": "<:aqwaxe:1532278309998559382>",
    "Dagger": "<:aqwdagger:1532278336687181934>",
    "Sword": "<:sword:1532256100756361257>",
    "Mace": "<:aqwmace:1532278402482966750>",
    "Staff": "<:aqwstaff:1532278486570369024>",
    "Wand": "<:aqwwand:1532278495156109482>",
    "Gun": "<:aqwgun:1532278392312041603>",
    "Polearm": "<:aqwpolearm:1532278411601514596>",
    "Bow": "<:aqwbow:1532278316630020127>",
    "Rifle": "<:aqwgun:1532278392312041603>",
    "Gauntlet": "<:aqwgauntlet:1532278386141954059>",
    "HandGun": "<:aqwgun:1532278392312041603>",
    "Whip": "<:aqwwhip:1532280038953586748>",
    "Armor": "<:armor:1532256090220138688>",
    "Class": "<:class:1532256037216976916>",
    "Cape": "<:cape:1532256092027879526>",
    "Helm": "<:helm:1532256093881761932>",
    "Pet": "<:pet:1532256098625523722>",
    "Quest Item": "<:scroll:1532256096063062157>",
    "Item": "<:misc:1532256591141929031>",
    "Misc": "<:aqwnecklace:1532278409583919104>",
    "Wall Item": "<:wall:1532255983873818778>",
    "House": "<:aqwhouse:1532278397575893063>",
    "Floor Item": "<:aqwfloor:1532278339233124512>",
}

def get_package_display_name(package):
    shops = package.get("shops", [])

    if not shops:
        return None

    name = shops[0].get("name")

    if not name:
        return None

    return name.removesuffix(" (Shop)")


def get_package(package_name: str):
    if package_name in BONUS_PACKAGES:
        return BONUS_PACKAGES[package_name]

    package_name = package_name.casefold()

    for package in BONUS_PACKAGES.values():
        display_name = get_package_display_name(package)

        if (
            display_name
            and display_name.casefold() == package_name
        ):
            return package

    return None


def get_package_items(package_name: str):
    package = get_package(package_name)

    if not package:
        return []

    items = []
    seen_urls = set()

    for shop in package.get("shops", []):
        for item in shop.get("items", []):
            url = item.get("url")

            if not url or url in seen_urls:
                continue

            seen_urls.add(url)
            items.append(item)

    return items


class BonusPackageView(discord.ui.LayoutView):

    def __init__(
        self,
        package_name: str,
        *,
        timeout: float = 300,
    ):
        super().__init__(timeout=timeout)

        self.package_name = package_name
        self.items = get_package_items(package_name)
        self.page = 0

        self.pages = max(
            1,
            math.ceil(len(self.items) / PAGE_SIZE),
        )

        # Create buttons BEFORE building the layout.
        self.previous_button = discord.ui.Button(
            label="Previous",
            emoji="◀️",
            style=discord.ButtonStyle.secondary,
            disabled=True,
        )

        self.next_button = discord.ui.Button(
            label="Next",
            emoji="▶️",
            style=discord.ButtonStyle.secondary,
            disabled=self.pages <= 1,
        )

        self.previous_button.callback = self.previous_callback
        self.next_button.callback = self.next_callback

        self.build_layout()

    def get_page_items(self):
        start = self.page * PAGE_SIZE
        end = start + PAGE_SIZE

        return self.items[start:end]

    def get_display_name(self):
        package = get_package(self.package_name)

        if package:
            name = get_package_display_name(package)

            if name:
                return name

        return self.package_name

    def build_layout(self):
        # LayoutView can only have one top-level container in this setup.
        container = discord.ui.Container(
            accent_colour=discord.Colour(7344907),
        )

        # Header
        container.add_item(
            discord.ui.TextDisplay(
                content=(
                    f"# {self.get_display_name()}\n"
                    f"**{len(self.items)} items** • "
                    f"Page **{self.page + 1} / {self.pages}**"
                )
            )
        )

        container.add_item(
            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.small,
            )
        )

        # Items
        for item in self.get_page_items():

            name = item.get(
                "name",
                "Unknown Item",
            )

            wiki_url = item.get("url")
            image_url = item.get("imageUrl")

            item_type = item.get("Type")
            icon = ITEM_ICONS.get(item_type, "")

            content = f"{icon}**{name}**"

            if wiki_url:
                content += f"\n[🔗 AQW Wiki]({wiki_url})"

            if image_url:
                section = discord.ui.Section(
                    discord.ui.TextDisplay(
                        content=content
                    ),
                    accessory=discord.ui.Thumbnail(
                        media=image_url
                    ),
                )
            else:
                section = discord.ui.TextDisplay(
                        content=content
                    )


            container.add_item(section)
            container.add_item(
                discord.ui.Section(
                    discord.ui.TextDisplay(
                        content=content
                    ),
                    accessory=self.create_item_button(item)
                )
            )

            container.add_item(
                discord.ui.Separator(
                    visible=True,
                    spacing=discord.SeparatorSpacing.small,
                )
            )

        # Pagination
        container.add_item(
            discord.ui.ActionRow(
                self.previous_button,
                self.next_button,
            )
        )

        self.add_item(container)

    def rebuild(self):
        self.clear_items()

        self.previous_button.disabled = self.page <= 0
        self.next_button.disabled = self.page >= self.pages - 1

        self.build_layout()

    async def previous_callback(
        self,
        interaction: discord.Interaction,
    ):
        if self.page <= 0:
            await interaction.response.defer()
            return

        self.page -= 1

        self.rebuild()

        await interaction.response.edit_message(
            view=self,
        )

    def create_item_button(self, item):
        name = item.get("name", "Unknown Item")

        button = discord.ui.Button(
            label="Preview",
            emoji="🎭",
            style=discord.ButtonStyle.secondary,
        )

        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()

            image = await render_png(
                interaction.user.display_name,
                item.get("name"),
                item.get("File"),
                item.get("Link"),
                item.get("Type"),
            )

            image.seek(0)

            await interaction.channel.send(
                file=discord.File(
                    image,
                    filename="preview.png",
                )
            )

        button.callback = callback

        return button

    async def next_callback(
        self,
        interaction: discord.Interaction,
    ):
        if self.page >= self.pages - 1:
            await interaction.response.defer()
            return

        self.page += 1

        self.rebuild()

        await interaction.response.edit_message(
            view=self,
        )

async def package_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:

    current = current.casefold()

    choices = []

    for package in BONUS_PACKAGES.values():
        display_name = get_package_display_name(package)

        if not display_name:
            continue

        if current not in display_name.casefold():
            continue

        choices.append(
            app_commands.Choice(
                name=display_name[:100],
                value=display_name,
            )
        )

        if len(choices) >= 25:
            break

    return choices
