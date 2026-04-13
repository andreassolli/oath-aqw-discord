import random


async def deal():
    user_cards = []
    dealer_cards = []

    deck = [(suit, value) for suit in range(1, 5) for value in range(2, 15)]
    random.shuffle(deck)

    user_cards = [deck.pop(), deck.pop()]
    dealer_cards = [deck.pop(), deck.pop()]

    return {"user": user_cards, "dealer": dealer_cards, "deck": deck}


async def get_value(cards):
    sum_x = 0
    sum_y = 0
    for card in cards:
        sum_x += card[1]
        if card[1] == 14:
            sum_y += 1
            sum_x += 11
        elif card[1] >= 10 and card[1] <= 13:
            sum_y += card[10]
        else:
            sum_y += card[1]
    return {"sum_x": sum_x, "sum_y": sum_y}


async def add_card(cards, deck):
    cards.append(deck.pop())
    return {"user": cards, "deck": deck}


async def add_dealer_card(cards, deck):
    dealer_values = await get_value(cards)

    if dealer_values.get("sum_y", 0) <= 16 and dealer_values.get("sum_x", 0) <= 16:
        (dealer, deck) = await add_card(cards, deck)
        return {"dealer": dealer, "deck": deck}
    else:
        return {"dealer": cards, "deck": deck}
