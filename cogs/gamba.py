from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from config import BETA_TESTER_ROLE_ID, BETA_TESTING_CHANNEL_ID, OFFICER_ROLE_ID
from economy.gamba.beg import beg
from economy.gamba.coinflip import run_coinflip
from economy.gamba.utils import lock_coins
from economy.gamba.yanken_accept_view import RPSAcceptView
from firebase_client import db


class Gamba(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="flip",
        description="Flip a coin, either against the house or challenge someone",
    )
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
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
        success, error = lock_coins(interaction.user.id, wager)

        if not success:
            return await interaction.response.send_message(error, ephemeral=True)

        await run_coinflip(interaction, wager, call, opponent)

    @app_commands.command(
        name="janken",
        description="Challenge someone to Rock Paper Scissors",
    )
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
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
    @app_commands.checks.has_role(BETA_TESTER_ROLE_ID)
    async def beg_command(self, interaction: discord.Interaction):

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


async def setup(bot: commands.Bot):
    await bot.add_cog(Gamba(bot))
