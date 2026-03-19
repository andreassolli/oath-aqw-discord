import discord
from discord import app_commands
from discord.ext import commands

from config import (
    BOT_GUY_ROLE_ID,
    COMMUNITY_FEEDBACK_CHANNEL_ID,
    DISCORD_MANAGER_ROLE_ID,
    GUILD_ID,
    MODERATOR_ROLE_ID,
)
from firebase_client import db

ALLOWED_ROLES = {BOT_GUY_ROLE_ID, MODERATOR_ROLE_ID, DISCORD_MANAGER_ROLE_ID}


class CloseReportView(discord.ui.View):
    def __init__(self, cog, user_id: int):
        super().__init__(timeout=None)
        self.cog = cog
        self.user_id = user_id

    @discord.ui.button(label="Close Report", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        thread = interaction.channel

        # Remove from memory
        self.cog.active_reports.pop(self.user_id, None)

        # Update Firestore
        db.collection("reports").document(str(self.user_id)).update({"open": False})

        # Lock thread
        await thread.edit(archived=True, locked=True)

        # Notify user
        user = interaction.client.get_user(self.user_id)
        if user:
            await user.send("🔒 Your report has been closed.")

        await interaction.response.send_message("Report closed.", ephemeral=True)


class Reports(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.waiting_for_report = {}
        self.active_reports = {}  # user_id -> thread_id

    async def cog_load(self):
        docs = db.collection("reports").stream()

        for doc in docs:
            data = doc.to_dict()
            if data.get("open"):
                self.active_reports[int(doc.id)] = int(data["thread_id"])

    @app_commands.command(name="report", description="Send in a semi-anonymous report.")
    async def report(self, interaction: discord.Interaction, topic: str):
        user = interaction.user

        # Prevent duplicate
        doc = db.collection("reports").document(str(user.id)).get()
        if doc.exists and doc.to_dict().get("open"):
            await interaction.response.send_message(
                "You already have an open report.", ephemeral=True
            )
            return

        try:
            dm = await user.create_dm()
            await dm.send(
                "📩 Please provide information about what you are reporting.\n*Everything you send in is anonymous, however if needed, the admins of the discord are able to check who sent it in the database.*"
            )

            self.waiting_for_report[user.id] = topic

            await interaction.response.send_message("Check your DMs!", ephemeral=True)

        except discord.Forbidden:
            await interaction.response.send_message(
                "I couldn't DM you. Please enable DMs.", ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            user_id = message.author.id
            if user_id in self.waiting_for_report:
                topic = self.waiting_for_report.pop(user_id)

                guild = self.bot.get_guild(GUILD_ID)
                channel = guild.get_channel(COMMUNITY_FEEDBACK_CHANNEL_ID)

                if not isinstance(channel, discord.ForumChannel):
                    return

                thread_obj = await channel.create_thread(
                    name=f"Report - {topic}", content=message.content
                )

                thread = thread_obj.thread

                self.active_reports[user_id] = thread.id

                db.collection("reports").document(str(user_id)).set(
                    {
                        "thread_id": thread.id,
                        "guild_id": guild.id,
                        "channel_id": channel.id,
                        "open": True,
                    }
                )

                db.collection("threads").document(str(thread.id)).set(
                    {"user_id": user_id}
                )

                # Send message + attachments
                files = [await a.to_file() for a in message.attachments]

                await thread.send(f"💬 Reporter: {message.content}", files=files)

                await thread.send(
                    "An officer will assist you shortly.",
                    view=CloseReportView(self, user_id),
                )

                await message.author.send("✅ Your report has been submitted!")
                return

            doc = db.collection("reports").document(str(user_id)).get()
            if not doc.exists:
                return

            report = doc.to_dict()
            if not report.get("open"):
                return

            thread = self.bot.get_channel(int(report["thread_id"]))
            if not thread:
                db.collection("reports").document(str(user_id)).delete()
                return

            files = [await a.to_file() for a in message.attachments]

            await thread.send(f"💬 Reporter: {message.content}", files=files)

        elif isinstance(message.channel, discord.Thread):
            thread = message.channel

            doc = db.collection("threads").document(str(thread.id)).get()
            if not doc.exists:
                return

            user_id = doc.to_dict()["user_id"]

            doc = db.collection("reports").document(str(user_id)).get()
            if not doc.exists:
                return

            report = doc.to_dict()
            if not report.get("open"):
                return

            if not any(role.id in ALLOWED_ROLES for role in message.author.roles):
                return

            user = self.bot.get_user(int(user_id))
            if not user:
                return

            files = [await a.to_file() for a in message.attachments]

            await user.send(f"💬 Officer: {message.content}", files=files)


async def setup(bot: commands.Bot):
    await bot.add_cog(Reports(bot))
