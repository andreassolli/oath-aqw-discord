import discord

from economy.gamba.blackjack import add_card, add_dealer_card, get_value
from economy.gamba.generate_blackjack import generate_blackjack


class BlackjackView(discord.ui.View):
    def __init__(self, user, dealer, deck):
        super().__init__()
        self.user = user
        self.dealer = dealer
        self.deck = deck
        self.locked = False
        self.message = None

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.user, self.deck = await add_card(self.user, self.deck)
        buffer = await generate_blackjack(self.user, self.dealer)
        file = discord.File(buffer, filename="table.png")

        user_total = await get_value(self.user)

        if user_total > 21:
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

            if dealer_total > 21:
                result = "<:GoobHeart:1459836996381048863> Dealer busted, you win!"
            elif dealer_total > user_total:
                result = "<:GoobCrying:1457956174174617651> Dealer wins"
            elif dealer_total < user_total:
                result = "<:GoobHeart:1459836996381048863> You win!"
            else:
                result = "<:mapClown:1484474701798707240> Push"

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
        self.dealer, self.deck = await add_dealer_card(self.dealer, self.deck)

        user_total = await get_value(self.user)
        dealer_total = await get_value(self.dealer)

        if dealer_total > 21:
            result = "Dealer busted, you win 🎉"
        elif dealer_total > user_total:
            result = "Dealer wins 😢"
        elif dealer_total < user_total:
            result = "You win 🎉"
        else:
            result = "Push 🤝"

        self.stop()
        self.locked = False
        return await interaction.response.send_message(
            content=f"{result}\nYou: {user_total} | Dealer: {dealer_total}"
        )

    @discord.ui.button(label="Surrender", style=discord.ButtonStyle.danger)
    async def surrender(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):

        self.stop()
        return await interaction.response.send_message(
            content="You surrendered and lost half your coins."
        )
