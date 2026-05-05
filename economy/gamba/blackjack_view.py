from io import BytesIO

import discord
from google.cloud import firestore

from economy.gamba.blackjack import add_card, add_dealer_card, get_value
from economy.gamba.generate_blackjack import BG, CARD_BACK, CARD_CACHE
from economy.gamba.utils import unlock_coins
from firebase_client import db


class BlackjackView(discord.ui.View):
    def __init__(self, user, dealer, deck, wager):
        super().__init__()
        self.user = user
        self.dealer = dealer
        self.deck = deck
        self.wager = wager

        self.locked = False
        self.has_hit = False
        self.message = None

        self.table_image = BG.copy()
        self._render_table()

    async def payout(self, user_id, amount):
        db.collection("users").document(str(user_id)).update(
            {"coins": firestore.Increment(amount)}
        )

    # Render table

    def _render_table(self, hide_dealer=True):
        self.table_image = BG.copy()

        # Player cards
        for i, card in enumerate(self.user):
            img = CARD_CACHE[card]
            self.table_image.paste(img, (58 + i * 117, 254), img)

        # Dealer cards
        for i, card in enumerate(self.dealer):
            img = CARD_BACK if hide_dealer and i > 0 else CARD_CACHE[card]
            self.table_image.paste(img, (58 + i * 117, 52), img)

    def _to_file(self):
        buffer = BytesIO()
        self.table_image.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename="table.png")

    # Helper functions

    def disable_surrender(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.label == "Surrender":
                child.disabled = True

    async def dealer_turn(self):
        self.dealer, self.deck = await add_dealer_card(self.dealer, self.deck)
        self._render_table(hide_dealer=False)

    async def resolve_game(self, user_total, dealer_total, blackjack=False):
        unlock_coins(self.user.id, self.wager)

        if dealer_total > 21:
            await self.payout(self.user.id, self.wager)
            return (
                f"<:GoobHeart:1459836996381048863> Dealer busted, "
                f"you won <:oathcoin:1462999179998531614>{self.wager * 2}!"
            )

        if dealer_total > user_total:
            await self.payout(self.user.id, -self.wager)
            return (
                f"<:GoobCrying:1457956174174617651> Dealer wins, "
                f"you lost <:oathcoin:1462999179998531614>{self.wager}..."
            )

        if dealer_total < user_total:
            payout = int(self.wager * 1.5) if blackjack else self.wager
            winnings = int(self.wager * 2.5) if blackjack else self.wager * 2

            await self.payout(self.user.id, payout)

            if blackjack:
                return (
                    f"<:GoobShock:1463149045731299328> Blackjack! You won "
                    f"<:oathcoin:1462999179998531614>{winnings}!"
                )
            else:
                return (
                    f"<:GoobHeart:1459836996381048863> You won "
                    f"<:oathcoin:1462999179998531614>{winnings}!"
                )

        return (
            f"<:mapClown:1484474701798707240> Push, "
            f"gained back <:oathcoin:1462999179998531614>{self.wager}"
        )

    async def finish_game(self, result, user_total, dealer_total):
        self.stop()
        await self.message.edit(
            content=f"{result}\nYou: {user_total} | Dealer: {dealer_total}",
            attachments=[self._to_file()],
            view=None,
        )

    # Buttons

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        self.user, self.deck = await add_card(self.user, self.deck)
        self.has_hit = True
        self.disable_surrender()

        self._render_table()
        file = self._to_file()

        user_total = await get_value(self.user)

        # Bust
        if user_total > 21:
            unlock_coins(self.user.id, self.wager)
            await self.payout(self.user.id, -self.wager)

            self.stop()
            return await self.message.edit(
                content=f"<:GoobCrying:1457956174174617651> You busted with {user_total}, "
                f"and lost <:oathcoin:1462999179998531614>{self.wager}",
                view=None,
                attachments=[file],
            )

        # Blackjack
        if user_total == 21:
            await self.dealer_turn()
            dealer_total = await get_value(self.dealer)

            result = await self.resolve_game(user_total, dealer_total, blackjack=True)
            return await self._finish_game(result, user_total, dealer_total)

        # Continue game
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

        await self.dealer_turn()
        dealer_total = await get_value(self.dealer)

        result = await self.resolve_game(user_total, dealer_total)
        await self.finish_game(result, user_total, dealer_total)

        self.locked = False

    @discord.ui.button(label="Surrender", style=discord.ButtonStyle.danger)
    async def surrender(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.has_hit:
            return await interaction.response.send_message(
                "You can only surrender before taking a hit.", ephemeral=True
            )

        unlock_coins(self.user.id, self.wager)
        await self.payout(self.user.id, -(self.wager // 2))

        self.stop()
        await interaction.response.edit_message(
            content=f"You surrendered and got back {self.wager // 2}.",
            view=None,
        )
