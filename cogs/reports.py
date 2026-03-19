import discord
from discord import app_commands
from discord.ext import commands

from config import (
    ADMIN_ROLE_ID,
    BOT_GUY_ROLE_ID,
    COMMUNITY_FEEDBACK_CHANNEL_ID,
    GUILD_ID,
    MAPRIL_ROLE_ID,
    MODERATOR_ROLE_ID,
    OFFICER_ROLE_ID,
    REPORT_TAG_ID,
    SOLVED_TAG_ID,
    UNSOLVED_TAG_ID,
)
from firebase_client import db


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

        # --- TAG HANDLING ---
        if isinstance(thread.parent, discord.ForumChannel):
            current_tags = thread.applied_tags
            new_tags = [tag for tag in current_tags if tag.id != UNSOLVED_TAG_ID]

            # Optional: add solved tag
            solved_tag = discord.utils.get(
                thread.parent.available_tags, id=SOLVED_TAG_ID
            )
            if solved_tag:
                new_tags.append(solved_tag)

            await thread.edit(applied_tags=new_tags)

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

            if not data.get("open"):
                continue

            user_id = int(doc.id)
            thread_id = int(data["thread_id"])

            self.active_reports[user_id] = thread_id

            thread = self.bot.get_channel(thread_id)
            if not thread:
                continue

            guild = self.bot.get_guild(data["guild_id"])
            if not guild:
                continue

            officer_role = guild.get_role(OFFICER_ROLE_ID)
            if not officer_role:
                continue

            # 🔁 Send NEW control message every restart
            msg = await thread.send(
                f"{officer_role.mention}, bot just restarted, and report still open.\nUse the button below to close it.",
                view=CloseReportView(self, user_id),
            )

            pins = await thread.pins()

            # Remove old bot control messages (optional logic)
            for p in pins:
                if p.author == self.bot.user:
                    try:
                        await p.unpin()
                    except:
                        pass

            await msg.pin()

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
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.author.bot:
            return

        # Ignore no actual change
        if before.content == after.content and before.attachments == after.attachments:
            return

        if isinstance(after.channel, discord.DMChannel):
            user_id = after.author.id

            doc = db.collection("reports").document(str(user_id)).get()
            if not doc.exists:
                return

            report = doc.to_dict()
            if not report.get("open"):
                return

            thread = self.bot.get_channel(int(report["thread_id"]))
            if not thread:
                return

            files = [await a.to_file() for a in after.attachments]

            await thread.send(f"✏️ **Reporter edited:**\n{after.content}", files=files)

        elif isinstance(after.channel, discord.Thread):
            thread = after.channel

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

            # Restrict to staff
            if not any(role.id == OFFICER_ROLE_ID for role in after.author.roles):
                return

            user = self.bot.get_user(int(user_id))
            if not user:
                return

            files = [await a.to_file() for a in after.attachments]
            role = "Officer"
            if any(role.id == ADMIN_ROLE_ID for role in after.author.roles):
                role = "Co-Leader"
            elif any(
                role.id == {MAPRIL_ROLE_ID, BOT_GUY_ROLE_ID}
                for role in after.author.roles
            ):
                role = "Head Officer"

            await user.send(f"✏️ **{role} edited:**\n{after.content}", files=files)

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
                report_tag = discord.utils.get(channel.available_tags, id=REPORT_TAG_ID)
                unsolved_tag = discord.utils.get(
                    channel.available_tags, id=UNSOLVED_TAG_ID
                )

                tags = [tag for tag in [report_tag, unsolved_tag] if tag is not None]

                thread_obj = await channel.create_thread(
                    name=f"Report - {topic}",
                    content=message.content,
                    applied_tags=tags,
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
                officer_role = guild.get_role(OFFICER_ROLE_ID)
                if not officer_role:
                    return
                await thread.send(
                    f"{officer_role.mention}, new report!.",
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

            if not any(role.id == OFFICER_ROLE_ID for role in message.author.roles):
                return

            user = self.bot.get_user(int(user_id))
            if not user:
                return

            files = [await a.to_file() for a in message.attachments]
            role = "Officer"
            if any(role.id == ADMIN_ROLE_ID for role in message.author.roles):
                role = "Co-Leader"
            elif any(
                role.id == {MAPRIL_ROLE_ID, BOT_GUY_ROLE_ID}
                for role in message.author.roles
            ):
                role = "Head Officer"

            await user.send(f"💬 {role}: {message.content}", files=files)


async def setup(bot: commands.Bot):
    await bot.add_cog(Reports(bot))
