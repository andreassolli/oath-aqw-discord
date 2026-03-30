from datetime import datetime, timedelta

import aiohttp
import discord

from config import TICKET_INSPECTORS_CHANNEL_ID
from firebase_client import db
from ticket_help.utils.qualify_helper import SteadyRateLimiter, verify_helper

# Temporary storage
user_responses = {}

QUESTIONS_STEP1 = [
    "Q1: Classes & Taunt Strategy\nWhat essential classes do you want for Speaker, and why do a 3 man over 4 man taunt?",
    "Q2: Zone Rotation\nWhy do we have to rotate who takes the zone, and why can there only be one at a time?",
    "Q3: Maximize APs debuffs, and Regeneration\nHow do you maximize APs Seal & Broken Seal debuff, and how do you avoid Speaker regenerating?",
    "Q4: Taunting as Lord of Order\nWhat do you have to do when taunting as LoO to avoid being stuck in the zone?",
    "Q5: Mana Issues and skill 5, Lord of Order\nWhy do you have to save skill 5 as Lord of Order, and how do you avoid mana issues?",
]

QUESTIONS_STEP2 = [
    "Q6: Taunting Pattern\nHow and when to taunt against Ultra Gramiel, and how long should you wait after Phase 1 to taunt?",
    "Q7: Haste Debuff, Phase 1\nHow do you end up with haste debuff during the 1st phase?",
    "Q8: Legion Revenant Enhancements & Avoid\nWhat enhancements do you need to have for Legion Revenant, and what do you have to avoid doing?",
    "Q9: Taunting Pattern, Phase 2\nHow do you loop the taunts in second phase, and ideally what order should each class taunt?",
    "Q10: Death's Door & Liberator Servants\nIf the text about 'Death's Door' appears before 'Liberator' text, what should you do?",
]


# ---------------- MODAL 1 ---------------- #
class FirstModal(discord.ui.Modal, title="Part 1 - Ultra Speaker"):
    q1 = discord.ui.TextInput(
        label="Q1: Classes & Taunt Strategy",
        placeholder="What essential classes do you want for Speaker, and why do a 3 man over 4 man taunt?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q2 = discord.ui.TextInput(
        label="Q2: Zone Rotation",
        placeholder="Why do we have to rotate who takes the zone, and why can there only be one at a time?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q3 = discord.ui.TextInput(
        label="Q3: Maximize APs debuffs, and Regeneration",
        placeholder="How do you maximize APs Seal & Broken Seal debuff, and how do you avoid Speaker regenerating?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q4 = discord.ui.TextInput(
        label="Q4: Taunting as Lord of Order",
        placeholder="What do you have to do when taunting as LoO to avoid being stuck in the zone?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q5 = discord.ui.TextInput(
        label="Q5: Mana Issues and skill 5, Lord of Order",
        placeholder="Why do you have to save skill 5 as Lord of Order, and how do you avoid mana issues?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_responses[interaction.user.id] = {
            "step1": [
                self.q1.value,
                self.q2.value,
                self.q3.value,
                self.q4.value,
                self.q5.value,
            ]
        }

        await interaction.response.send_message(
            "Part 1 - Ultra Speaker completed. Click below for the second and final part, Ultra Gramiel.",
            view=NextStepView(),
            ephemeral=True,
        )


# ---------------- MODAL 2 ---------------- #
class SecondModal(discord.ui.Modal, title="Step 2 - Ultra Gramiel"):
    q6 = discord.ui.TextInput(
        label="Q6: Taunting Pattern",
        placeholder="How and when to taunt against Ultra Gramiel, and how long should you wait after Phase 1 to taunt?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q7 = discord.ui.TextInput(
        label="Q7: Haste Debuff, Phase 1",
        placeholder="How do you end up with haste debuff during the 1st phase?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q8 = discord.ui.TextInput(
        label="Q8: Legion Revenant Enhancements & Avoid",
        placeholder="What enhancements do you need to have for Legion Revenant, and what do you have to avoid doing?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q9 = discord.ui.TextInput(
        label="Q9: Taunting Pattern, Phase 2",
        placeholder="How do you loop the taunts in second phase, and ideally what order should each class taunt?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    q10 = discord.ui.TextInput(
        label="Q10: Death's Door & Liberator Servants",
        placeholder="If the text about 'Death's Door' appears before 'Liberator' text, what should you do?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        data = user_responses.get(interaction.user.id, {})

        data["step2"] = [
            self.q6.value,
            self.q7.value,
            self.q8.value,
            self.q9.value,
            self.q10.value,
        ]
        guild = interaction.guild
        if not guild:
            return await interaction.followup.send(
                "❌ Something went wrong (no server).",
                ephemeral=True,
            )
        channel = guild.get_channel(TICKET_INSPECTORS_CHANNEL_ID)

        if not channel or not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send(
                "❌ Application channel not found.",
                ephemeral=True,
            )
        # Create thread
        try:
            thread = await channel.create_thread(
                name=f"Application from {interaction.user.display_name}",
                type=discord.ChannelType.public_thread,
            )

            await thread.send(f"**{interaction.user.display_name}'s application**")

            for q, ans in zip(QUESTIONS_STEP1, data["step1"]):
                await thread.send(f"**{q}**\n{ans}")

            for q, ans in zip(QUESTIONS_STEP2, data["step2"]):
                await thread.send(f"**{q}**\n{ans}")

        except Exception as e:
            return await interaction.followup.send(
                f"❌ Failed to create application: {e}",
                ephemeral=True,
            )

        db.collection("users").document(str(interaction.user.id)).set(
            {
                "last_application_at": discord.utils.utcnow(),
            },
            merge=True,
        )

        # Cleanup
        user_responses.pop(interaction.user.id, None)

        await interaction.followup.send(
            "✅ Submission complete! A Ticket Inspector will review your application.",
            ephemeral=True,
        )


class StartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Start application",
        style=discord.ButtonStyle.primary,
        custom_id="start_application_button",
    )
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_ref = db.collection("users").document(str(interaction.user.id))
        doc = user_ref.get()
        data = doc.to_dict() or {}

        last_app = data.get("last_application_at")
        if last_app:
            now = discord.utils.utcnow()
            if now - last_app < timedelta(days=3):
                remaining = timedelta(days=3) - (now - last_app)
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                return await interaction.response.send_message(
                    f"⏳ Wait {remaining.days}d {hours}h {minutes}m...",
                    ephemeral=True,
                )

        return await interaction.response.send_modal(FirstModal())

        # ccid = data.get("ccid")
        # if not ccid:
        #    return await interaction.response.send_message(
        #        "❌ You must verify first.",
        #        ephemeral=True,
        #    )

        # async with aiohttp.ClientSession() as session:
        #    limiter = SteadyRateLimiter(0.3)
        #    result = await verify_helper(session, limiter, ccid)

        # if result["qualified"]:
        #    user_ref.set({"qualified_helper": True}, merge=True)
        #    return await interaction.response.send_modal(FirstModal())

        # missing = []
        # if not result["weapon"]:
        #     missing.append(
        #         "❌ Missing any 51% damage Weapon<:swordaqw:1487004634307629056>"
        #     )
        # if not result["classes"]:
        #     missing.append(
        #         "❌ Missing Lord of Order and/or ArchPaladin<:classbadge:1471256107057156117>"
        #     )
        # if not result["taunt"]:
        #     missing.append(
        #         "❌ Missing Scroll of Enrage<:scrollaqw:1487000863867277432>"
        #     )
        # if not result["potion"]:
        #     missing.append("❌ Missing Potions<:potion:1457810711706341544>")
        # if not result["blade of awe"]:
        #    missing.append("❌ Missing Awe Enhancements<:swordaqw:1487004634307629056>")

        # await interaction.response.send_message(
        #     "❌ You are not qualified to apply yet:\n" + "\n".join(missing),
        #     ephemeral=True,
        # )


class NextStepView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Part 2",
        style=discord.ButtonStyle.success,
        custom_id="application_part2_button",
    )
    async def next_step(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # Disable button
        button.disabled = True

        self.stop()  # optional, prevents further interaction handling

        await interaction.response.send_modal(SecondModal())

        await interaction.message.edit(view=self)
