import discord

from firebase_client import db

BADGE_EMOJIS = {
    "Beta Tester White": "<:oathbeta:1487777899938320496>",
    "Beta Tester Black": "<:oathbeta:1487777899938320496>",
    "Beta Tester Green": "<:oathbeta:1487777899938320496>",
    "51% Weapons I": "<:weaponbadge:1471256072772915374>",
    "51% Weapons II": "<:weaponbadge:1471256072772915374>",
    "51% Weapons III": "<:weaponbadge:1471256072772915374>",
    "51% Weapons IV": "<:weaponbadge:1471256072772915374>",
    "Epic Journey I": "<:epicbadge:1471258940867346617>",
    "Epic Journey II": "<:epicbadge:1471258940867346617>",
    "Epic Journey III": "<:epicbadge:1471258940867346617>",
    "Epic Journey IV": "<:epicbadge:1471258940867346617>",
    "Achievement Badges I": "<:aqwbadge:1471256138799517853>",
    "Achievement Badges II": "<:aqwbadge:1471256138799517853>",
    "Achievement Badges III": "<:aqwbadge:1471256138799517853>",
    "Achievement Badges IV": "<:aqwbadge:1471256138799517853>",
    "Class Collector I": "<:classbadge:1471256107057156117>",
    "Class Collector II": "<:classbadge:1471256107057156117>",
    "Class Collector III": "<:classbadge:1471256107057156117>",
    "Class Collector IV": "<:classbadge:1471256107057156117>",
    "Whale I": "<:whalehd:1473998297227333734>",
    "Whale II": "<:whalehd:1473998297227333734>",
    "Whale III": "<:whalehd:1473998297227333734>",
    "Whale IV": "<:whalehd:1473998297227333734>",
    "Guild Founder": "<:oathcoin:1462999179998531614>",
    "AQW Founder": "<:aqwfounder:1471269208791978034>",
}

BADGES_DESCRIPTIONS = {
    "Beta Tester White": "Participated in Beta, and bought the White Beta Tester Card.",
    "Beta Tester Black": "Participated in Beta, and bought the Black Beta Tester Card.",
    "Beta Tester Green": "Participated in Beta, and bought the Green Beta Tester Card.",
    "51% Weapons I": "Obtain 7 unique 51% Weapons.",
    "51% Weapons II": "Obtain 15 unique 51% Weapons.",
    "51% Weapons III": "Obtain 25 unique 51% Weapons.",
    "51% Weapons IV": "Obtain almost **ALL** (32) 51% Weapons.",
    "Epic Journey I": "Obtain 16 unique Epic Journey Badges.",
    "Epic Journey II": "Obtain 23 unique Epic Journey Badges.",
    "Epic Journey III": "Obtain 30 unique Epic Journey Badges.",
    "Epic Journey IV": "Obtain **ALL** Epic Journey Badges.",
    "Achievement Badges I": "Obtain 150 Achievement Badges.",
    "Achievement Badges II": "Obtain 300 Achievement Badges.",
    "Achievement Badges III": "Obtain 450 Achievement Badges.",
    "Achievement Badges IV": "Obtain 600 Achievement Badges.",
    "Class Collector I": "Obtain 50 Classes, no duplicate names.",
    "Class Collector II": "Obtain 100 Classes, no duplicate names.",
    "Class Collector III": "Obtain 150 Classes, no duplicate names.",
    "Class Collector IV": "Obtain 200 Classes, no duplicate names.",
    "Whale I": "Obtain 150 combined Exclusive/Support/HeroMart Badges, and have 2 Upholder Badges.",
    "Whale II": "Obtain 200 combined Exclusive/Support/HeroMart Badges, have gifted more than 25 000 ACs during gifting event, and have 4 Upholder Badges.",
    "Whale III": "Obtain 250 combined Exclusive/Support/HeroMart Badges, have gifted more than 50 000 ACs during gifting event, have 4 Upholder Badges and one of the loyalty badges for either ACs, Membership or Years Played.",
    "Whale IV": "Obtain 300 combined Exclusive/Support/HeroMart Badges, an IODA in your inventory, have gifted more than 100 000 ACs during two gifting events, have 2 out of 3 of the loyalty badges, and have 8 Upholder Badges OR 3 out of 3 loyalty badges.",
    "Guild Founder": "Awarded to those who helped found or support the Oath discord server from the beginning.",
    "AQW Founder": "Awarded to those who have the founder or beta-tester badge in AQW.",
}


class ProfileView(discord.ui.View):
    def __init__(
        self,
        badges: list[str],
        is_potw: bool = False,
        has_been_potw: bool = False,
        name: str = "",
        wins: int = 0,
        show_beta: bool = False,
    ):
        super().__init__(timeout=None)
        self.badges = badges  # store badge info on the view
        self.is_potw = is_potw
        self.has_been_potw = has_been_potw
        self.name = name
        self.wins = wins
        if not show_beta:
            self.remove_item(self.view_participants)

    @discord.ui.button(label="View badges🎖️", style=discord.ButtonStyle.primary)
    async def view_badges(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button["ProfileView"],
    ):
        if not self.badges:
            await interaction.response.send_message(
                "This user has no badges yet.",
                ephemeral=True,
            )
            return

        badge_list = "\n".join(
            f"{BADGE_EMOJIS.get(badge, '')} **{badge}** — {BADGES_DESCRIPTIONS.get(badge, 'No description available')}"
            for badge in self.badges
        )

        if self.is_potw:
            potw_text = f"👑 {self.name} is currently **Player of the Week!** \n"
        elif self.has_been_potw:
            potw_text = f"<:potwBadge:1476938152861241565> {self.name} has previously been **Player of the Week!** \n"
        else:
            potw_text = ""

        if self.wins:
            win_text = f"🏆 {self.name} finished 1st during helper competition {self.wins} time(s)! \n"
        else:
            win_text = ""

        if win_text != "" or potw_text != "":
            extra_text = "\n"
        else:
            extra_text = ""

        await interaction.response.send_message(
            f"{potw_text}{win_text}{extra_text}🎖️ **Badges:**\n{badge_list}",
            ephemeral=True,
        )

    @discord.ui.button(label="🌐", style=discord.ButtonStyle.secondary)
    async def view_participants(self, interaction: discord.Interaction, _):

        participants = (
            db.collection("users").where("beta_participant", "==", True).stream()
        )

        participants = [p.to_dict() or {} for p in participants]

        if not participants:
            await interaction.response.send_message(
                "No participants yet.",
                ephemeral=True,
            )
            return

        beta_list = "\n".join(
            f"{p.get('aqw_username') or p.get('username') or 'Unknown'}"
            for p in participants[:100]
        )

        await interaction.response.send_message(
            f"**<:oathbeta:1487777899938320496>Everyone who participated in the beta, we appreciate all `{len(participants)}` of you!**\n{beta_list}",
            ephemeral=True,
        )
