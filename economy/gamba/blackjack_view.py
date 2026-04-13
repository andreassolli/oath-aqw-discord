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

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user, self.deck = await add_card(self.user, self.deck)
        buffer = await generate_blackjack(self.user, self.dealer)
        file = discord.File(buffer, filename="table.png")

        user_total = await get_value(self.user)

        if user_total > 21:
            self.stop()
            return await interaction.response.edit_message(
                content=f"You busted with {user_total} 💀", view=None
            )
        elif user_total == 21:
            self.dealer, self.deck = await add_dealer_card(self.dealer, self.deck)

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
            return await interaction.response.edit_message(
                content=f"{result}\nYou: {user_total} | Dealer: {dealer_total}",
                view=None,
            )

        await interaction.response.edit_message(
            content=f"You: {self.user} ({user_total})\nDealer: [hidden], {self.dealer[1]}",
            view=self,
            file=file,
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
        return await interaction.response.edit_message(
            content=f"{result}\nYou: {user_total} | Dealer: {dealer_total}", view=None
        )

    @discord.ui.button(label="Surrender", style=discord.ButtonStyle.danger)
    async def surrender(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.locked:
            return await interaction.response.send_message(
                "Please wait for the dealer's turn.", ephemeral=True
            )
        self.locked = True
        self.stop()
        await interaction.response.edit_message(
            content="You surrendered and lost half your coins.", view=None
        )
        self.locked = False
