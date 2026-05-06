from io import BytesIO

import discord
from google.cloud import firestore

from economy.gamba.blackjack import add_card, add_dealer_card, get_value
from economy.gamba.generate_blackjack import (
    BG,
    CARD_BACK,
    CARD_CACHE,
)
from economy.gamba.utils import lock_coins, unlock_coins
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
        self.has_hit = False
        self.table_image = BG.copy()
        self.draw_initial_cards()

    async def payout(self, user_id, amount):
        user_ref = db.collection("users").document(str(user_id))
        user_ref.set(
            {
                "coins": firestore.Increment(amount),
                "current_blackjack": {
                    "user_cards": [{"suit": c[0], "value": c[1]} for c in self.user],
                    "dealer_cards": [
                        {"suit": c[0], "value": c[1]} for c in self.dealer
                    ],
                    "wager": self.wager,
                    "deck": [{"suit": c[0], "value": c[1]} for c in self.deck],
                    "status": "completed",
                },
            },
            merge=True,
        )

    def render_table(self, hide_dealer=True):
        self.table_image = BG.copy()

        for i, card in enumerate(self.user):
            self.table_image.paste(
                CARD_CACHE[card],
                (58 + i * 117, 254),
                CARD_CACHE[card],
            )

        for i, card in enumerate(self.dealer):
            img = CARD_BACK if hide_dealer and i > 0 else CARD_CACHE[card]
            self.table_image.paste(img, (58 + i * 117, 52), img)

    def draw_initial_cards(self):
        for i, card in enumerate(self.user):
            img = CARD_CACHE[card]
            self.table_image.paste(img, (58 + i * 117, 254), img)

        for i, card in enumerate(self.dealer):
            if i == 0:
                img = CARD_CACHE[card]
                self.table_image.paste(img, (58 + i * 117, 52), img)
            else:
                self.table_image.paste(CARD_BACK, (58 + i * 117, 52), CARD_BACK)

    # Display board
    def to_file(self):
        buffer = BytesIO()
        self.table_image.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename="table.png")

    # Whenever your turn is over
    async def dealer_draws(self, user_id, user_total: int):
        # Dealer draws until 17+
        dealer_total = get_value(self.dealer)

        while dealer_total < 17:
            self.dealer, self.deck = add_dealer_card(self.dealer, self.deck)
            dealer_total = get_value(self.dealer)

        self.render_table(hide_dealer=False)
        file = self.to_file()

        # Release wager lock now that round is over
        unlock_coins(user_id, self.wager)

        if dealer_total > 21:
            # Return wager + winnings
            await self.payout(user_id, self.wager)
            result = (
                f"<:GoobHeart:1459836996381048863> Dealer busted! "
                f"You won <:oathcoin:1462999179998531614>{self.wager}!"
            )

        elif dealer_total > user_total:
            result = (
                f"<:GoobCrying:1457956174174617651> Dealer wins. "
                f"You lost <:oathcoin:1462999179998531614>{self.wager}."
            )

        elif dealer_total < user_total:
            # Standard win pays 1:1
            await self.payout(user_id, self.wager)
            result = (
                f"<:GoobShock:1463149045731299328> You won "
                f"<:oathcoin:1462999179998531614>{self.wager}!"
            )

        else:
            # Push = refund wager
            await self.payout(user_id, self.wager)
            result = f"<:mapClown:1484474701798707240> Push. Your wager was returned."

        return result, file, dealer_total

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.user, self.deck = add_card(self.user, self.deck)
        self.has_hit = True
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.label == "Surrender":
                child.disabled = True
        new_card = self.user[-1]
        img = CARD_CACHE[new_card]

        self.table_image.paste(img, (58 + (len(self.user) - 1) * 117, 254), img)

        file = self.to_file()

        user_total = get_value(self.user)

        if user_total > 21:
            unlock_coins(interaction.user.id, self.wager)
            await self.payout(interaction.user.id, -self.wager)
            self.stop()
            return await self.message.edit(
                content=f"<:GoobCrying:1457956174174617651> You busted with {user_total}, and lost <:oathcoin:1462999179998531614>{self.wager}",
                view=None,
                attachments=[file],
            )
        elif user_total == 21:
            result, file, dealer_total = await self.dealer_draws(
                interaction.user.id, user_total
            )
            self.stop()
            return await self.message.edit(
                content=f"{result}\nYou: {user_total} | Dealer: {dealer_total}",
                view=None,
                attachments=[file],
            )

        # No blackjack or bust, continue
        user_ref = db.collection("users").document(str(interaction.user.id))
        user_ref.set(
            {
                "current_blackjack": {
                    "user_cards": [{"suit": c[0], "value": c[1]} for c in self.user],
                    "dealer_cards": [
                        {"suit": c[0], "value": c[1]} for c in self.dealer
                    ],
                    "wager": self.wager,
                    "deck": [{"suit": c[0], "value": c[1]} for c in self.deck],
                    "status": "ongoing",
                }
            },
            merge=True,
        )

        await self.message.edit(
            content=f"Your cards: {user_total}",
            view=self,
            attachments=[file],
        )

    @discord.ui.button(label="Double", style=discord.ButtonStyle.success)
    async def double(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer()

        # Check if the user has already hit
        if self.has_hit:
            return await interaction.followup.send(
                "You can only double down before hitting.", ephemeral=True
            )

        # Add a check for if the user has enough coins to double down
        success, error = lock_coins(interaction.user.id, self.wager)
        if not success:
            return await interaction.followup.send(
                "You do not have enough coins to double.", ephemeral=True
            )

        self.wager = self.wager * 2
        self.user, self.deck = add_card(self.user, self.deck)
        new_card = self.user[-1]
        img = CARD_CACHE[new_card]

        self.table_image.paste(img, (58 + (len(self.user) - 1) * 117, 254), img)

        file = self.to_file()

        user_total = get_value(self.user)

        # Player Busted after doubling down
        if user_total > 21:
            unlock_coins(interaction.user.id, self.wager)
            await self.payout(interaction.user.id, -self.wager)
            self.stop()
            return await self.message.edit(
                content=f"<:GoobCrying:1457956174174617651> You busted with {user_total}, and lost the double down <:oathcoin:1462999179998531614>{self.wager}",
                view=None,
                attachments=[file],
            )
        # House Plays out their hand
        else:
            result, file, dealer_total = await self.dealer_draws(
                interaction.user.id, user_total
            )
            self.stop()
            return await self.message.edit(
                content=f"{result}\nYou: {user_total} | Dealer: {dealer_total}",
                view=None,
                attachments=[file],
            )

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.primary)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.locked:
            return await interaction.response.send_message(
                "Please wait for the dealer's turn.", ephemeral=True
            )

        await interaction.response.defer()
        self.locked = True

        user_total = get_value(self.user)

        result, file, dealer_total = await self.dealer_draws(
            interaction.user.id, user_total
        )

        self.stop()
        self.locked = False

        await self.message.edit(
            content=f"{result}\nYou: {user_total} | Dealer: {dealer_total}",
            attachments=[file],
            view=None,
        )

    @discord.ui.button(label="Surrender", style=discord.ButtonStyle.danger)
    async def surrender(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.has_hit:
            return await interaction.response.send_message(
                "You can only surrender before taking a hit.", ephemeral=True
            )

        # Return half the wager
        unlock_coins(interaction.user.id, self.wager)
        await self.payout(interaction.user.id, -(self.wager // 2))

        self.stop()
        await interaction.response.edit_message(
            content=f"You surrendered and got back {self.wager // 2}.", view=None
        )
