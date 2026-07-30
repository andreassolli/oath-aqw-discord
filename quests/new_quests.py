import discord

from firebase_client import db
from quests.setup_quests import setup_quests
from google.cloud import firestore

ITEM_TYPES = {
    "Axe": "<:aqwaxe:1532278309998559382> Axe",
    "Dagger": "<:aqwdagger:1532278336687181934> Dagger",
    "Sword": "<:sword:1532256100756361257> Sword",
    "Mace": "<:aqwmace:1532278402482966750> Mace",
    "Staff": "<:aqwstaff:1532278486570369024> Staff",
    "Wand": "<:aqwwand:1532278495156109482> Wand",
    "Gun": "<:aqwgun:1532278392312041603>Gun",
    "Polearm": "<:aqwpolearm:1532278411601514596> Polearm",
    "Bow": "<:aqwbow:1532278316630020127> Bow",
    "Rifle": "<:aqwgun:1532278392312041603> Rifle",
    "Gauntlet": "<:aqwgauntlet:1532278386141954059> Gauntlet",
    "HandGun": "<:aqwgun:1532278392312041603> HandGun",
    "Whip": "<:aqwwhip:1532280038953586748> Whip",
    "Armor": "<:armor:1532256090220138688> Armor",
    "Class": "<:class:1532256037216976916> Class",
    "Cape": "<:cape:1532256092027879526> Cape",
    "Helm": "<:helm:1532256093881761932> Helm",
    "Pet": "<:pet:1532256098625523722> Pet",
    "Quest Item": "<:scroll:1532256096063062157> Quest Item",
    "Item": "<:misc:1532256591141929031> Item",
    "Misc": "<:aqwnecklace:1532278409583919104> Misc",
    "Wall Item": "<:wall:1532255983873818778> Wall Item",
    "House": "<:aqwhouse:1532278397575893063> House",
    "Floor Item": "<:aqwfloor:1532278339233124512> Floor Item",
}

OPTIONS = [
    discord.SelectOption(
        label=label,
        value=value,
    )
    for value, label in ITEM_TYPES.items()
]


class ChangeQuestModal(discord.ui.Modal, title="Change Quest Items"):
    def __init__(self, bot, quest_ref, quest_name: str):
        super().__init__()

        self.bot = bot
        self.quest_ref = quest_ref
        self.quest_name = quest_name

        # Load existing items
        existing = [
            doc.to_dict()
            for doc in quest_ref.collection("items").stream()
        ]

        while len(existing) < 3:
            existing.append({})

        # Item 1
        self.item1 = discord.ui.TextInput(
            label="Item 1",
            required=False,
            default=existing[0].get("name", ""),
            max_length=100,
        )
        self.type1 = discord.ui.Label(
            text="Type 1",
            component=discord.ui.Select(
                placeholder=existing[0].get("type", "Select type"),
                options=OPTIONS,
            ),
        )

        # Item 2
        self.item2 = discord.ui.TextInput(
            label="Item 2",
            required=False,
            default=existing[1].get("name", ""),
            max_length=100,
        )
        self.type2 = discord.ui.Label(
            text="Type 2",
            component=discord.ui.Select(
                placeholder=existing[1].get("type", "Select type"),
                options=OPTIONS,
            ),
        )

        # Item 3
        self.item3 = discord.ui.TextInput(
            label="Item 3",
            required=False,
            default=existing[2].get("name", ""),
            max_length=100,
        )
        self.type3 = discord.ui.Label(
            text="Type 3",
            component=discord.ui.Select(
                placeholder=existing[2].get("type", "Select type"),
                options=OPTIONS,
            ),
        )

        self.add_item(self.item1)
        self.add_item(self.type1)

        self.add_item(self.item2)
        self.add_item(self.type2)

        self.add_item(self.item3)
        self.add_item(self.type3)

    async def on_submit(self, interaction: discord.Interaction):
        # Remove existing items
        for doc in self.quest_ref.collection("items").stream():
            doc.reference.delete()

        entries = [
            ("Item 1", self.item1.value.strip(), self.type1.component.values),
            ("Item 2", self.item2.value.strip(), self.type2.component.values),
            ("Item 3", self.item3.value.strip(), self.type3.component.values),
        ]


        for label, name, selected in entries:
            if name and not selected:
                return await interaction.response.send_message(
                    f"Please choose a type for **{label}**.",
                    ephemeral=True,
                )
            if not name or not selected:
                continue

            self.quest_ref.collection("items").add(
                {
                    "name": name,
                    "type": selected[0],
                }
            )

        # Reset progress for this quest
        await reset_quest_progress(self.quest_name)

        await setup_quests(self.bot)

        await interaction.response.send_message(
            f"✅ Updated **{self.quest_name}** and reset its progress for all users.",
            ephemeral=True,
        )


async def reset_quest_progress(quest_name: str):
    batch = db.batch()
    writes = 0

    for user in db.collection("users").stream():
        data = user.to_dict() or {}

        if quest_name not in data.get("quests_completed", []):
            continue

        batch.update(
            user.reference,
            {
                "quests_completed": firestore.ArrayRemove([quest_name]),
            },
        )

        writes += 1

        if writes >= 500:
            batch.commit()
            batch = db.batch()
            writes = 0

    if writes:
        batch.commit()
