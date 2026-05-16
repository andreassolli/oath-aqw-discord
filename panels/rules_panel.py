import discord

from config import SPAM_CMD_CHANNEL_ID


async def setup_rules(client: discord.Client):
    channel = client.get_channel(SPAM_CMD_CHANNEL_ID)

    if not channel:
        print("❌ Ticket panel channel not found. Check TICKET_CHANNEL_ID.")
        return

    await channel.send(view=RulesLayout())


class RulesLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__()

        self.container2 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/rules.png",
                ),
            ),
            discord.ui.Separator(visible=False, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content="These are our server guidelines. Any misconduct or failure to comply will result in sanctions, varying by severity and whether it's a repeated offense."
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:leftwing:1505157673249935402><:rule1w:1505157671836454972><:rightwing:1505157674776531015> **No hate speech or political harassment**"
            ),
            discord.ui.TextDisplay(
                content="> Refrain from controversial or offensive subjects. No slurs, this goes for all types of slurs, whether related to someones sexuality or ethnicity."
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:leftwing:1505157673249935402><:rule2w:1505157669995151381><:rightwing:1505157674776531015>** No NSFW content should be posted**"
            ),
            discord.ui.TextDisplay(
                content="> Adult language may be used but it should not make others uncomfortable, nor be excessive in topic or duration. Officers reserve the right to determine when a conversation has gotten out of hand."
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:leftwing:1505157673249935402><:rule3w:1505157669017751592><:rightwing:1505157674776531015>** Follow the law, server guidelines, and Discord policies**"
            ),
            discord.ui.TextDisplay(
                content="> No illegal activity or actions that would compromise other uses. This also involves any encouragement towards these types of actions, as well as any form of doxxing."
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:leftwing:1505157673249935402><:rule4w:1505157667893543033><:rightwing:1505157674776531015>** No breaking AQW Terms of Service, or promoting services/behaviors that does**"
            ),
            discord.ui.TextDisplay(
                content="> E.g botting, account selling or sharing. Failure to comply will result in you being kicked from the guild.\n> We believe in second chances, which is why you may apply to join after a 30 day period has passed. However, failure to comply after given a second chance will make you permanently banned from the guild."
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:leftwing:1505157673249935402><:rule5w:1505157666740375632><:rightwing:1505157674776531015>** Avoid poor player etiquette**"
            ),
            discord.ui.TextDisplay(
                content="> Refrain from behavior that would be considered trolling or abuse, both in game and in discord activties. Failure to comply may result in temporary to permanent loss of ability to both request help and to help others."
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503698816300351648> **Make sure to report any misconduct**"
            ),
            discord.ui.TextDisplay(
                content="> If you see any misconduct, make sure to report it to us by doing `/report`. These reports are semi-anonymous, meaning no one sees who sent any report or messages, unless it is suspected of being a false report."
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bright_separator.png",
                ),
            ),
            accent_colour=discord.Colour(7344907),
        )

        self.add_item(self.container2)
