from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from google.cloud import firestore

from config import (
    BETA_TESTER_ROLE_ID,
    BETA_TESTING_CHANNEL_ID,
    BOT_GUY_ROLE_ID,
    OFFICER_ROLE_ID,
)
from economy.gamba.beg import beg
from economy.gamba.blackjack import add_card, deal, get_value
from economy.gamba.blackjack_view import BlackjackView
from economy.gamba.coinflip import run_coinflip
from economy.gamba.generate_blackjack import generate_blackjack
from economy.gamba.utils import lock_coins, unlock_coins
from economy.gamba.yanken_accept_view import RPSAcceptView
from firebase_client import db


class Gamba(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="flip",
        description="Flip a coin, either against the house or challenge someone",
    )
    async def coinflip_command(
        self,
        interaction: discord.Interaction,
        wager: int,
        call: Literal["Heads", "Tails"] | None = None,
        opponent: discord.Member | None = None,
    ):
        channel_id = interaction.channel_id
        if channel_id and channel_id != BETA_TESTING_CHANNEL_ID:
            guild = interaction.guild
            if not guild:
                return
            channel = guild.get_channel(BETA_TESTING_CHANNEL_ID)
            if channel:
                return await interaction.response.send_message(
                    f"You have to use this command in {channel.mention}"
                )
        if wager <= 0:
            return await interaction.response.send_message(
                "You cannot wager a negative amount.",
                ephemeral=True,
            )
        if wager > 25000:
            return await interaction.followup.send(
                "Wager must be below <:oathcoin:1462999179998531614>25 000.",
                ephemeral=True,
            )
        success, error = lock_coins(interaction.user.id, wager)

        if not success:
            return await interaction.response.send_message(error, ephemeral=True)

        await run_coinflip(interaction, wager, call, opponent)

    @app_commands.command(
        name="janken",
        description="Challenge someone to Rock Paper Scissors",
    )
    async def rps(
        self,
        interaction: discord.Interaction,
        wager: int,
        opponent: discord.Member,
    ):

        channel_id = interaction.channel_id
        if channel_id and channel_id != BETA_TESTING_CHANNEL_ID:
            guild = interaction.guild
            if not guild:
                return
            channel = guild.get_channel(BETA_TESTING_CHANNEL_ID)
            if channel:
                return await interaction.response.send_message(
                    f"You have to use this command in {channel.mention}"
                )
        if wager <= 0:
            return await interaction.response.send_message(
                "You cannot wager a negative amount.",
                ephemeral=True,
            )
        if wager > 25000:
            return await interaction.followup.send(
                "Wager must be below <:oathcoin:1462999179998531614>25 000.",
                ephemeral=True,
            )
        if opponent == interaction.user:
            await interaction.response.send_message(
                "You can't challenge yourself.",
                ephemeral=True,
            )
            return
        doc = db.collection("users").document(str(interaction.user.id)).get()
        coins = doc.to_dict().get("coins", 0) if doc else 0
        success, error = lock_coins(interaction.user.id, wager)

        if not success:
            return await interaction.response.send_message(error, ephemeral=True)
        if coins < wager:
            return await interaction.response.send_message(
                f"You don't have enough coins to wager {wager}.",
                ephemeral=True,
            )
        view = RPSAcceptView(
            challenger=interaction.user,
            opponent=opponent,
            wager=wager,
        )

        embed = discord.Embed(
            title="<:gon:1480922691950088293> Rock Paper Scissors",
            description=f"{interaction.user.mention} challenged {opponent.mention}!\nWager: <:oathcoin:1462999179998531614> {wager}",
            color=discord.Color.orange(),
        )
        embed.set_thumbnail(
            url="https://static.wikia.nocookie.net/disneythehunchbackofnotredame/images/f/f4/Jan_gu.jpg/revision/latest/scale-to-width-down/284?cb=20140413215313"
        )

        await interaction.response.send_message(
            embed=embed,
            view=view,
        )

        view.message = await interaction.original_response()
        return

    @app_commands.command(name="beg", description="Beg the other users for some money")
    async def beg_command(self, interaction: discord.Interaction):
        if interaction.channel_id != BETA_TESTING_CHANNEL_ID:
            allowed_mentions = f"<#{BETA_TESTING_CHANNEL_ID}>"

            await interaction.followup.send(
                f"❌ This command can only be used in {allowed_mentions}.",
                ephemeral=True,
            )
            return
        guild = interaction.guild
        if not guild:
            return

        user = guild.get_member(interaction.user.id)
        if not user:
            return

        embed, view = await beg(user)

        if not embed:
            return await interaction.response.send_message(view, ephemeral=True)

        await interaction.response.send_message(embed=embed, view=view)

        message = await interaction.original_response()
        view.message = message

    @app_commands.command(
        name="slots", description="Gamble your coins in the slots machine"
    )
    @app_commands.checks.has_role(OFFICER_ROLE_ID)
    async def slots_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="This is a loop, it never ends",
            description="Just for testing purposes",
            color=discord.Color.blue(),
        )
        file = discord.File("assets/finaly.gif", filename="finaly.gif")
        embed.set_image(url="attachment://finaly.gif")
        await interaction.response.send_message(embed=embed, file=file)

    @app_commands.command(
        name="blackjack", description="Play blackjack with the house."
    )
    async def blackjack_command(self, interaction: discord.Interaction, wager: int):
        await interaction.response.defer(ephemeral=True)
        if wager < 1:
            return await interaction.followup.send(
                "Wager must be at least <:oathcoin:1462999179998531614>1.",
                ephemeral=True,
            )
        if wager > 25000:
            return await interaction.followup.send(
                "Wager must be below <:oathcoin:1462999179998531614>25 000.",
                ephemeral=True,
            )
        success, error = lock_coins(interaction.user.id, wager)

        if not success:
            return await interaction.followup.send(error, ephemeral=True)

        user, dealer, deck = await deal()
        user_total = await get_value(user)
        dealer_total = await get_value(dealer)

        if user_total == 21:
            user_ref = db.collection("users").document(str(interaction.user.id))
            buffer = await generate_blackjack(user, dealer, True)
            await interaction.edit_original_response(
                content=f"Blackjack! You win <:oathcoin:1462999179998531614>{int(wager * 2.5)}",
                attachments=[discord.File(buffer, filename="table.png")],
            )
            unlock_coins(interaction.user.id, wager)

            if dealer_total == 21:
                result = f"<:mapClown:1484474701798707240> Push, gained back <:oathcoin:1462999179998531614>{wager}"

            else:
                user_ref.update({"coins": firestore.Increment(int(wager * 1.5))})
                result = f"<:GoobShock:1463149045731299328> Blackjack! You win <:oathcoin:1462999179998531614>{int(wager * 2.5)}"

            return await interaction.followup.send(
                f"{result}\nYour cards: {user_total} | Dealer: {dealer_total}",
                ephemeral=True,
            )

        user_string = f"Your cards: {user_total}"
        view = BlackjackView(user, dealer, deck, wager)
        file = view._to_file()
        msg = await interaction.followup.send(
            f"{user_string}",
            view=view,
            file=file,
        )
        view.message = msg
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Gamba(bot))
