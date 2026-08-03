import discord
from discord.ui import Button, View

from config import BETA_TESTER_ROLE_ID
from quests.utils import check_for_quest_completion


class QuestCheckButton(Button):
    def __init__(self):
        super().__init__(
            label="🧳 Check Inventory",
            style=discord.ButtonStyle.green,
            custom_id="quest_check_button",
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if not interaction.guild:
            return await interaction.followup.send(
                "This can only be used in a server.", ephemeral=True
            )

        user_id = interaction.user.id

        result = await check_for_quest_completion(user_id)

        await interaction.followup.send(
            result,
            ephemeral=True,
        )


class QuestView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(QuestCheckButton())
