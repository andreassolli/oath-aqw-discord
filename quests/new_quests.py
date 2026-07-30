import discord

from firebase_client import db
from quests.setup_quests import refresh_quests
from google.cloud import firestore

ITEM_TYPES = {
    "Axe": (
        "Axe",
        discord.PartialEmoji(name="aqwaxe", id=1532278309998559382),
    ),
    "Dagger": (
        "Dagger",
        discord.PartialEmoji(name="aqwdagger", id=1532278336687181934),
    ),
    "Sword": (
        "Sword",
        discord.PartialEmoji(name="sword", id=1532256100756361257),
    ),
    "Mace": (
        "Mace",
        discord.PartialEmoji(name="aqwmace", id=1532278402482966750),
    ),
    "Staff": (
        "Staff",
        discord.PartialEmoji(name="aqwstaff", id=1532278486570369024),
    ),
    "Wand": (
        "Wand",
        discord.PartialEmoji(name="aqwwand", id=1532278495156109482),
    ),
    "Gun": (
        "Gun",
        discord.PartialEmoji(name="aqwgun", id=1532278392312041603),
    ),
    "Polearm": (
        "Polearm",
        discord.PartialEmoji(name="aqwpolearm", id=1532278411601514596),
    ),
    "Bow": (
        "Bow",
        discord.PartialEmoji(name="aqwbow", id=1532278316630020127),
    ),
    "Rifle": (
        "Rifle",
        discord.PartialEmoji(name="aqwgun", id=1532278392312041603),
    ),
    "Gauntlet": (
        "Gauntlet",
        discord.PartialEmoji(name="aqwgauntlet", id=1532278386141954059),
    ),
    "HandGun": (
        "HandGun",
        discord.PartialEmoji(name="aqwgun", id=1532278392312041603),
    ),
    "Whip": (
        "Whip",
        discord.PartialEmoji(name="aqwwhip", id=1532280038953586748),
    ),
    "Armor": (
        "Armor",
        discord.PartialEmoji(name="armor", id=1532256090220138688),
    ),
    "Class": (
        "Class",
        discord.PartialEmoji(name="class", id=1532256037216976916),
    ),
    "Cape": (
        "Cape",
        discord.PartialEmoji(name="cape", id=1532256092027879526),
    ),
    "Helm": (
        "Helm",
        discord.PartialEmoji(name="helm", id=1532256093881761932),
    ),
    "Pet": (
        "Pet",
        discord.PartialEmoji(name="pet", id=1532256098625523722),
    ),
    "Quest Item": (
        "Quest Item",
        discord.PartialEmoji(name="scroll", id=1532256096063062157),
    ),
    "Item": (
        "Item",
        discord.PartialEmoji(name="misc", id=1532256591141929031),
    ),
    "Misc": (
        "Misc",
        discord.PartialEmoji(name="aqwnecklace", id=1532278409583919104),
    ),
    "Wall Item": (
        "Wall Item",
        discord.PartialEmoji(name="wall", id=1532255983873818778),
    ),
    "House": (
        "House",
        discord.PartialEmoji(name="aqwhouse", id=1532278397575893063),
    ),
    "Floor Item": (
        "Floor Item",
        discord.PartialEmoji(name="aqwfloor", id=1532278339233124512),
    ),
}

OPTIONS = [
    discord.SelectOption(
        label=label,
        value=value,
        emoji=emoji,
    )
    for value, (label, emoji) in ITEM_TYPES.items()
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

        self.add_item(self.item1)
        self.add_item(self.type1)

        self.add_item(self.item2)
        self.add_item(self.type2)

    async def on_submit(self, interaction: discord.Interaction):
        # Remove existing items
        await interaction.response.defer(ephemeral=True)
        for doc in self.quest_ref.collection("items").stream():
            doc.reference.delete()

        entries = [
            ("Item 1", self.item1.value.strip(), self.type1.component.values),
            ("Item 2", self.item2.value.strip(), self.type2.component.values),
        ]


        for label, name, selected in entries:
            if name and not selected:
                return await interaction.followup.send(
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

        await refresh_quests(self.bot)

        await interaction.followup.send(
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
