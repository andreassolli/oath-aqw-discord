import discord

ITEMS_PER_PAGE = 50


ITEM_TO_ICON = {
    "Armor": "<:aqwArmor:1487000736087670936>",
    "Class": "<:aqwClass:1501670684101840906>",
    "Axe": "<:aqwAxe:1487000523268947988>",
    "Dagger": "<:aqwDagger:1487000631653961779>",
    "Sword": "<:aqwSword:1501670723708780586>",
    "Bow": "<:aqwBow:1487000684204265533>",
    "Cape": "<:aqwCape:1501670762174746644>",
    "Gauntlet": "<:aqwGauntlet:1487000801695109160>",
    "Helm": "<:aqwHelm:1487000474014974054>",
    "Mace": "<:aqwMace:1491408562231181353>",
    "Pet": "<:aqwPet:1491408513124008088>",
    "Polearm": "<:aqwSpear:1487000575290642553>",
    "Gun": "<:aqwGun:1533725133917782238>",
    "Rifle": "<:aqwGun:1533725133917782238>",
    "HandGun": "<:aqwGun:1533725133917782238>",
    "Staff": "<:aqwStaff:1533725354659680327>",
    "Wand": "<:aqwWand:1533725398523969667>",
    "Whip": "<:aqwGun:1533725133917782238>",
    "Misc": "<:aqwGround:1533725253019373599>",
    "Wall Item": "<:aqwWall:1533725458577752134>",
    "House": "<:aqwHouse:1533725178759090328>",
    "Floor Item": "<:aqwFloor:1533725305041322124>"
}

class IodaView(discord.ui.View):
    def __init__(self, items):
        super().__init__(timeout=600)

        self.items = items
        self.page = 0
        self.max_page = (len(items) - 1) // ITEMS_PER_PAGE

    def make_embed(self):
        start = self.page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE

        embed = discord.Embed(
            title="Most IoDA'ed Items",
            color=discord.Color.gold()
        )

        lines = []

        for i, item in enumerate(self.items[start:end], start=start + 1):
            lines.append(
                f"**#{i}** {ITEM_TO_ICON[item['Type']]}{item['Name']} — `{item['Count']:,}`"
            )

        embed.description = "\n".join(lines)

        embed.set_footer(
            text=f"Page {self.page + 1}/{self.max_page + 1}"
        )

        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1

        await interaction.response.edit_message(
            embed=self.make_embed(),
            view=self
        )

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.max_page:
            self.page += 1

        await interaction.response.edit_message(
            embed=self.make_embed(),
            view=self
        )
