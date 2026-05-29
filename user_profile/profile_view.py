import discord

from firebase_client import db

BADGE_EMOJIS = {
    "Beta Tester White": "<:betabadge:1509937421247053884>",
    "Beta Tester Black": "<:betabadge:1509937421247053884>",
    "Beta Tester Green": "<:betabadge:1509937421247053884>",
    "51% Weapons I": "<:weapons1:1509937632837107882>",
    "51% Weapons II": "<:weapons2:1509937636985278668>",
    "51% Weapons III": "<:weapons3:1509937638839419010>",
    "51% Weapons IV": "<:weapons4:1509937640575733904>",
    "Epic Journey I": "<:epic1:1509937526901571695>",
    "Epic Journey II": "<:epic2:1509937528470376589>",
    "Epic Journey III": "<:epic3:1509937529703366686>",
    "Epic Journey IV": "<:epic4:1509937530982891540>",
    "Achievement Badges I": "<:aqwbadges1:1509937425710055544>",
    "Achievement Badges II": "<:aqwbadges2:1509937417812054179>",
    "Achievement Badges III": "<:aqwbadges3:1509937418638331935>",
    "Achievement Badges IV": "<:aqwbadges4:1509937420106203368>",
    "Class Collector I": "<:class1:1509937422522388623>",
    "Class Collector II": "<:class2:1509937424296444086>",
    "Class Collector III": "<:class3:1509937649975169224>",
    "Class Collector IV": "<:class4:1509937525760987187>",
    "Whale I": "<:whale1:1509937642249392128>",
    "Whale II": "<:whale2:1509937643805216900>",
    "Whale III": "<:whale3:1509937645260767343>",
    "Whale IV": "<:whale4:1509937648783982622>",
    "Guild Founder": "<:founder:1509937460040171682>",
    "AQW Founder": "<:aqwfounder:1471269208791978034>",
    "Infinity: Funded it Myself!": "<:dollarbacker:1509215944445137016>",
    "Infinity Founder": "<:infinitybacker:1509215864220680272>",
    "Infinity Epic Founder": "<:epicbacker:1509216718873034923>",
    "Infinity Underworld Founder": "<:underworldbacker:1509215869778264206>",
    "Infinity Legendary Founder": "<:legendarybacker:1509215866204721372>",
    "Infinity Immortalized Founder": "<:immortalbacker:1509215862853468180>",
    "Infinity Benevolent Founder": "<:benevolentbacker:1509216002670596278>",
    "Infinity Weapon Designer": "<:weaponbacker:1509215871434752140>",
    "Infinity Set Designer": "<:armorbacker:1509216001185812611>",
    "Infinity Mysterious Founder": "<:mysteriousbacker:1509215867664339104>",
    "Oath Pillar": "<:pillar:1509937631465836714>",
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
    "Oath Pillar": "Awarded to those who keep Oath standing by donating at least $10 to events.",
    "Infinity: Funded it Myself!": "Awarded to those who supported AQW:Infinity with atleast $1 through the Kickstarter campaign.",
    "Infinity Founder": "Awarded to those who supported AQW:Infinity with atleast $25 through the Kickstarter campaign.",
    "Infinity Epic Founder": "Awarded to those who supported AQW:Infinity with atleast $50 through the Kickstarter campaign.",
    "Infinity Underworld Founder": "Awarded to those who supported AQW:Infinity with atleast $60 through the Kickstarter campaign.",
    "Infinity Legendary Founder": "Awarded to those who supported AQW:Infinity with atleast $125 through the Kickstarter campaign.",
    "Infinity Immortalized Founder": "Awarded to those who supported AQW:Infinity with atleast $250 through the Kickstarter campaign.",
    "Infinity Benevolent Founder": "Awarded to those who supported AQW:Infinity with atleast $400 through the Kickstarter campaign.",
    "Infinity Weapon Designer": "Awarded to those who supported AQW:Infinity with atleast $500 through the Kickstarter campaign.",
    "Infinity Set Designer": "Awarded to those who supported AQW:Infinity with atleast $1500 through the Kickstarter campaign.",
    "Infinity Mysterious Founder": "Awarded to those who supported AQW:Infinity with atleast $5000 through the Kickstarter campaign.",
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
            db.collection("users").where("participated_in_beta", "==", True).stream()
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
