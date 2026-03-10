import random


async def coinflip(fair: bool = False, heads: bool = True) -> str:
    toss = random.randint(1, 100)
    if fair:
        return "Heads" if toss <= 50 else "Tails"
    else:
        if heads:
            return "Heads" if toss <= 49 else "Tails"
        else:
            return "Tails" if toss <= 49 else "Heads"
