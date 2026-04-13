import discord

from economy.gamba.blackjack import add_card, add_dealer_card, get_value


class BlackjackView(discord.ui.View):
    def __init__(self, user, dealer, deck):
        super().__init__()
        self.user = user
        self.dealer = dealer
        self.deck = deck
        self.locked = False

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.locked:
            return await interaction.response.send_message(
                "Please wait for your card to be dealt.", ephemeral=True
            )
        self.locked = True
        (user, deck) = await add_card(self.user, self.deck)
        self.user = user
        (dealer, deck) = await add_dealer_card(self.dealer, deck)
        self.dealer = dealer
        self.deck = deck
        self.locked = False
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.primary)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.locked:
            return await interaction.response.send_message(
                "Please wait for the dealer's turn.", ephemeral=True
            )
        self.locked = True
        (dealer, deck) = await add_dealer_card(self.dealer, self.deck)
        self.dealer = dealer
        self.deck = deck
        self.locked = False
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Surrender", style=discord.ButtonStyle.danger)
    async def surrender(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.locked:
            return await interaction.response.send_message(
                "Please wait for the dealer's turn.", ephemeral=True
            )
        self.locked = True
        await interaction.response.send_message(
            "You have surrendered, and lost have of your wagered coins."
        )
        self.locked = False
        await interaction.response.edit_message(view=self)
