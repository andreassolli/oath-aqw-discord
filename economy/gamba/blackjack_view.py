import discord
from google.cloud import firestore

from economy.gamba.blackjack import add_card, add_dealer_card, get_value
from economy.gamba.generate_blackjack import generate_blackjack
from economy.gamba.utils import unlock_coins
from firebase_client import db


class BlackjackView(discord.ui.View):
    def __init__(self, user, dealer, deck, wager):
        super().__init__()
        self.user = user
        self.dealer = dealer
        self.deck = deck
        self.locked = False
        self.message = None
        self.wager = wager

    async def payout(self, user_id, amount):
        user_ref = db.collection("users").document(str(user_id))
        user_ref.update({"coins": firestore.Increment(amount)})

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.user, self.deck = await add_card(self.user, self.deck)
        buffer = await generate_blackjack(self.user, self.dealer)
        file = discord.File(buffer, filename="table.png")

        user_total = await get_value(self.user)

        if user_total > 21:
            unlock_coins(interaction.user.id, self.wager)
            await self.payout(interaction.user.id, -self.wager)
            self.stop()
            return await self.message.edit(
                content=f"<:GoobCrying:1457956174174617651> You busted with {user_total}",
                view=None,
                attachments=[file],
            )
        elif user_total == 21:
            self.dealer, self.deck = await add_dealer_card(self.dealer, self.deck)
            buffer = await generate_blackjack(self.user, self.dealer, True)
            file = discord.File(buffer, filename="table.png")
            dealer_total = await get_value(self.dealer)
            unlock_coins(interaction.user.id, self.wager)

            if dealer_total > 21:
                await self.payout(interaction.user.id, self.wager)
                result = f"<:GoobHeart:1459836996381048863> Dealer busted, you won, and got <:oathcoin:1462999179998531614>{self.wager * 2}!"

            elif dealer_total > user_total:
                result = f"<:GoobCrying:1457956174174617651> Dealer wins, you lost <:oathcoin:1462999179998531614>{self.wager}..."
                await self.payout(interaction.user.id, -self.wager)

            elif dealer_total < user_total:
                await self.payout(interaction.user.id, int(self.wager * 1.5))
                result = f"<:GoobShock:1463149045731299328> Blackjack! You won <:oathcoin:1462999179998531614>{int(self.wager * 2.5)}!"

            else:
                await self.payout(interaction.user.id, -self.wager)
                result = f"<:mapClown:1484474701798707240> Push, gained back <:oathcoin:1462999179998531614>{self.wager}"

            self.stop()
            return await self.message.edit(
                content=f"{result}\nYou: {user_total} | Dealer: {dealer_total}",
                view=None,
                attachments=[file],
            )

        await self.message.edit(
            content=f"Your cards: {user_total}",
            view=self,
            attachments=[file],
        )

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.primary)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.locked:
            return await interaction.response.send_message(
                "Please wait for the dealer's turn.", ephemeral=True
            )
        self.locked = True

        user_total = await get_value(self.user)
        dealer_total = await get_value(self.dealer)

        self.dealer, self.deck = await add_dealer_card(self.dealer, self.deck)
        buffer = await generate_blackjack(self.user, self.dealer, True)
        file = discord.File(buffer, filename="table.png")
        dealer_total = await get_value(self.dealer)
        unlock_coins(interaction.user.id, self.wager)
        if dealer_total > 21:
            await self.payout(interaction.user.id, self.wager)
            result = f"<:GoobHeart:1459836996381048863> Dealer busted, you won, and got <:oathcoin:1462999179998531614>{self.wager * 2}!"

        elif dealer_total > user_total:
            result = f"<:GoobCrying:1457956174174617651> Dealer wins, you lost <:oathcoin:1462999179998531614>{self.wager}..."
            await self.payout(interaction.user.id, -self.wager)
        elif dealer_total < user_total:
            await self.payout(interaction.user.id, self.wager)
            result = f"<:GoobHeart:1459836996381048863> You won, and got <:oathcoin:1462999179998531614>{self.wager * 2}!"

        else:
            await self.payout(interaction.user.id, -self.wager)
            result = f"<:mapClown:1484474701798707240> Push, gained back <:oathcoin:1462999179998531614>{self.wager}"

        self.stop()
        self.locked = False
        return await self.message.edit(
            content=f"{result}\nYou: {user_total} | Dealer: {dealer_total}",
            attachments=[file],
        )

    @discord.ui.button(label="Surrender", style=discord.ButtonStyle.danger)
    async def surrender(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        unlock_coins(interaction.user.id, self.wager)
        await self.payout(interaction.user.id, self.wager // 2)
        self.stop()
        return await interaction.response.edit_message(
            content=f"You surrendered and got back {self.wager // 2}."
        )
