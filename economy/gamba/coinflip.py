from typing import Literal

import discord
from google.cloud import firestore

from economy.gamba.coinflip_accept_view import CoinflipAcceptView
from economy.gamba.utils import coinflip, unlock_coins
from firebase_client import db


async def run_coinflip(
    interaction: discord.Interaction,
    wager: int,
    call: Literal["Heads", "Tails"] | None = None,
    opponent: discord.Member | None = None,
):

    heads_coin = "<:goobCoin:1480895675477524564>"
    tails_coin = "<:oathcoin:1462999179998531614>"

    if opponent is None:
        if call is None:
            await interaction.response.send_message(
                "You must choose Heads or Tails when flipping against the house.",
                ephemeral=True,
            )
            return

        heads = call == "Heads"

        result = await coinflip(fair=False, heads=heads)

        coin = heads_coin if result.lower() == "heads" else tails_coin
        win = result.lower() == call.lower()

        embed = discord.Embed(
            title=f"{tails_coin} Coinflip",
            color=discord.Color.green() if win else discord.Color.red(),
        )
        embed.add_field(
            name="Your Call",
            value=call.capitalize(),
            inline=True,
        )
        embed.add_field(
            name="Wager",
            value=f"<:oathcoin:1462999179998531614> {wager}",
            inline=False,
        )

        embed.add_field(
            name="Result",
            value=f"{coin} **{result.capitalize()}**",
            inline=False,
        )

        embed.add_field(
            name="Outcome",
            value="🏆 You win!"
            if win
            else "<:GoobShock:1463149045731299328> House wins!",
            inline=False,
        )

        points = wager if win else -wager
        user_ref = db.collection("users").document(str(interaction.user.id))

        unlock_coins(interaction.user.id, wager)

        user_ref.set({"coins": firestore.Increment(points)}, merge=True)

        await interaction.response.send_message(embed=embed)
        return

    if opponent == interaction.user:
        await interaction.response.send_message(
            "You can't challenge yourself.",
            ephemeral=True,
        )
        return

    if call is not None:
        await interaction.response.send_message(
            "You cannot call when flipping against a player. They will call themselves.",
            ephemeral=True,
        )
        return

    view = CoinflipAcceptView(
        challenger=interaction.user, opponent=opponent, wager=wager
    )

    embed = discord.Embed(
        title=f"{tails_coin} Coinflip Challenge",
        description=f"{interaction.user.mention} has challenged {opponent.mention} to a coinflip!",
        color=discord.Color.gold(),
    )
    embed.add_field(
        name="Wager",
        value=f"<:oathcoin:1462999179998531614> {wager}",
        inline=False,
    )

    embed.add_field(
        name="Next Step",
        value=f"{opponent.mention} must accept the challenge.",
        inline=False,
    )

    embed.set_footer(text="Opponent chooses Heads or Tails after accepting.")

    await interaction.response.send_message(
        embed=embed,
        view=view,
    )
