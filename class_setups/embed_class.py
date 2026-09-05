from typing import List

import discord
from PIL import Image
from io import BytesIO

BUTTONS_PER_ROW = 3

def get_emote(type: str):
    if "Scroll" in type:
        return "<:scroll:1532256096063062157>"
    elif "Potent" in type:
        return "<:potion:1457810711706341544>"
    elif "Philtre" in type:
        return "<:feli:1545785837457772644>"
    else:
        return "<:aqwwater:1532278500910694410>"


class ClassView(discord.ui.LayoutView):
    def __init__(
        self,
        class_name: str,
        general_loadout: dict[str, str],
        consumables: dict[str, str],
        class_image: Image.Image | None,
        boss_loadouts: dict[str, dict[str, str]] | None = None,
        description: str | None = None,
        is_class: bool = True,
    ):
        super().__init__(timeout=None)

        self.class_name = class_name
        self.general_loadout = general_loadout
        self.consumables = consumables
        self.class_image = class_image
        self.boss_loadouts = boss_loadouts or {}

        self.class_file = None

        if class_image:
            image_bytes = BytesIO()
            class_image.save(image_bytes, format="PNG")
            image_bytes.seek(0)

            self.class_file = discord.File(
                image_bytes,
                filename="class.png",
            )

        self.build_general_layout()

    def build_general_layout(self):
        components:List[discord.ui.Item] = [
            discord.ui.TextDisplay(
                content=f"## <:lvl:1545782330747256862> {self.class_name}"
            ),

            discord.ui.Separator(),

            discord.ui.TextDisplay(
                content=(
                    f"<:sword:1532256100756361257> "
                    f"{self.general_loadout.get('sword', '—')}\n"
                    f"<:class:1532256037216976916> "
                    f"{self.general_loadout.get('class', '—')}\n"
                    f"<:helm:1532256093881761932> "
                    f"{self.general_loadout.get('helm', '—')}\n"
                    f"<:cape:1532256092027879526> "
                    f"{self.general_loadout.get('cloak', '—')}"
                ),
            ),

            discord.ui.Separator(),

            discord.ui.TextDisplay(
                content=(
                    f"<:elixir:1457810755050143754> "
                    f"{self.consumables.get('elixir', '—')}\n"
                    f"<:Tonic:1457810787702935635> "
                    f"{self.consumables.get('tonic', '—')}\n"
                    f"{get_emote(self.consumables.get('consumable', '—'))} "
                    f"{self.consumables.get('consumable', '—')}"
                ),
            ),

            discord.ui.Separator(),
        ]

        # Boss buttons
        if self.boss_loadouts:
            buttons = [
                BossButton(
                    boss_name=boss_name,
                    class_name=self.class_name,
                    class_data=class_data,
                    selected=boss_name == "standard"
                )
                for boss_name, class_data in self.boss_loadouts.items()
            ]

            # Discord ActionRows can contain max 5 buttons
            for i in range(0, len(buttons), BUTTONS_PER_ROW):
                components.append(
                    discord.ui.ActionRow(
                        *buttons[i:i + BUTTONS_PER_ROW]
                    )
                )

        components.append(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="attachment://class.png",
                ),
            )
        )

        self.container1 = discord.ui.Container(
            *components,
            accent_colour=discord.Colour(7344907),
        )

        self.clear_items()
        self.add_item(self.container1)

    def show_boss_setup(
        self,
        *,
        boss_name: str,
        class_data: dict[str, str],
    ):
        components: List[discord.ui.Item] = [
            discord.ui.TextDisplay(
                content=f"## <:lvl:1545782330747256862> {self.class_name}"
            ),

            discord.ui.Separator(),

            discord.ui.TextDisplay(
                content=(
                    f"<:sword:1532256100756361257> "
                    f"{class_data.get('sword', '—')}\n"
                    f"<:class:1532256037216976916> "
                    f"{class_data.get('class', '—')}\n"
                    f"<:helm:1532256093881761932> "
                    f"{class_data.get('helm', '—')}\n"
                    f"<:cape:1532256092027879526> "
                    f"{class_data.get('cloak', '—')}"
                ),
            ),

            discord.ui.Separator(),

            discord.ui.TextDisplay(
                content=(
                    f"<:elixir:1457810755050143754> "
                    f"{class_data.get('elixir', '—')}\n"
                    f"<:Tonic:1457810787702935635> "
                    f"{class_data.get('tonic', '—')}\n"
                    f"{get_emote(self.consumables.get('consumable', '—'))} "
                    f"{class_data.get('consumable', '—')}"
                ),
            ),

            discord.ui.Separator(),
        ]

        # Add buttons again so the user can switch bosses
        buttons = [
            BossButton(
                boss_name=name,
                class_name=self.class_name,
                class_data=data,
                selected=name == boss_name
            )
            for name, data in self.boss_loadouts.items()
        ]

        for i in range(0, len(buttons), BUTTONS_PER_ROW):
            components.append(
                discord.ui.ActionRow(
                    *buttons[i:i + BUTTONS_PER_ROW]
                )
            )

        components.append(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="attachment://class.png",
                ),
            )
        )

        self.container1 = discord.ui.Container(
            *components,
            accent_colour=discord.Colour(7344907),
        )

        self.clear_items()
        self.add_item(self.container1)

class BossButton(discord.ui.Button):
    def __init__(
        self,
        *,
        boss_name: str,
        class_name: str,
        class_data: dict[str, str],
        selected,
    ):
        super().__init__(
            label=boss_name[:1].capitalize() + boss_name[1:],
            style=discord.ButtonStyle.success if selected else discord.ButtonStyle.secondary,
            emoji=discord.PartialEmoji(
                name="circlecheck" if selected else "circle",
                id=1545781307894792222 if selected else 1545781305512562779,
            ),
        )

        self.boss_name = boss_name
        self.class_name = class_name
        self.class_data = class_data

    async def callback(self, interaction: discord.Interaction):
        view = self.view

        if not isinstance(view, ClassView):
            return await interaction.response.send_message(
                "❌ Unable to update this class view.",
                ephemeral=True,
            )

        view.show_boss_setup(
            boss_name=self.boss_name,
            class_data=self.class_data,
        )

        await interaction.response.edit_message(
            view=view,
        )
