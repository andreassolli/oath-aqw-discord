import random


async def deal():
    user_cards = []
    dealer_cards = []

    deck = [(suit, value) for suit in range(1, 5) for value in range(2, 15)]
    random.shuffle(deck)

    user_cards = [deck.pop(), deck.pop()]
    dealer_cards = [deck.pop(), deck.pop()]

    return user_cards, dealer_cards, deck


async def get_value(cards):
    total = 0
    aces = 0

    for _, value in cards:
        if value >= 11 and value <= 13:
            total += 10
        elif value == 14:
            total += 11
            aces += 1
        else:
            total += value

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total


async def add_card(cards, deck):
    cards.append(deck.pop())
    return cards, deck


async def add_dealer_card(cards, deck):
    while await get_value(cards) < 17:
        cards, deck = await add_card(cards, deck)
    return cards, deck
