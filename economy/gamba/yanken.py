from typing import Literal


async def rock_paper_scissor(
    choice1: Literal["Rock", "Paper", "Scissors"],
    choice2: Literal["Rock", "Paper", "Scissors"],
):

    if choice1 == choice2:
        return "Draw"

    wins = {
        "Rock": "Scissors",
        "Paper": "Rock",
        "Scissors": "Paper",
    }

    return choice1 if wins[choice1] == choice2 else choice2
