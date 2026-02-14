import discord

class RoomCopyView(discord.ui.View):
    def __init__(self, room: str):
        super().__init__(timeout=None)
        self.room = room

    @discord.ui.button(label="📋 Copy Room", style=discord.ButtonStyle.secondary)
    async def copy_room(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(
            f"📋 **Room code:**\n```{self.room}```",
            ephemeral=True
        )
