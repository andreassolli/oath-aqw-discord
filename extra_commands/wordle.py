import datetime
import random

import discord

from config import LOBBY_CHANNEL_ID
from extra_commands.wordle_share import generate_wordle_share
from firebase_client import db

KEYBOARD_ROWS = [
    "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM",
]


def build_keyboard(letter_states: dict[str, str]) -> str:
    rows = []

    for row in KEYBOARD_ROWS:
        formatted = []
        for char in row:
            state = letter_states.get(char.lower())

            if state == "correct":
                formatted.append(f"**{char}**")
            elif state == "present":
                formatted.append(f"__{char}__")
            elif state == "wrong":
                formatted.append(f"~~{char}~~")
            else:
                formatted.append(char)

        rows.append(" ".join(formatted))

    return "\n".join(rows)


class ShareWordleView(discord.ui.View):
    def __init__(self, guesses, guess_count):
        super().__init__(timeout=None)
        self.guesses = guesses
        self.guess_count = guess_count

    @discord.ui.button(label="Share Result", style=discord.ButtonStyle.green)
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Generate board image
        board_image = await generate_wordle_share(interaction=interaction)
        file = discord.File(board_image, filename="aqwordle.png")
        channel_id = interaction.channel_id
        guild = interaction.guild
        if guild is None or channel_id is None:
            return
        channel = guild.get_channel(channel_id)
        if channel is None:
            return
        # Build embed
        embed = discord.Embed(
            title="AQWordle Completed!",
            description=(
                f"✅ **{interaction.user.display_name} completed today's AQWordle!**\n\n"
                f"Join them using `/aqwordle` in {channel.mention}"
            ),
            color=0x00FF00,
        )

        embed.set_image(url="attachment://aqwordle.png")
        embed.set_footer(text=f"Solved in {self.guess_count}/6 guesses")

        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "❌ Guild not found.",
                ephemeral=True,
            )
            return

        channel = guild.get_channel(LOBBY_CHANNEL_ID)

        if channel is None:
            await interaction.response.send_message(
                "❌ Lobby channel not found.",
                ephemeral=True,
            )
            return

        # Send to lobby channel
        await channel.send(embed=embed, file=file)

        # Confirm to user
        await interaction.response.send_message(
            "✅ Your result has been shared in the lobby!",
            ephemeral=True,
        )


def create_wordle_embed(user_id: str):
    wordle_word = get_wordle_word()
    if wordle_word is None:
        return None

    embed = discord.Embed(
        title="Wordle", description=f"Guess the word in 6 tries", color=0x00FF00
    )
    embed.set_footer(text=f"User ID: {user_id}")

    return embed


def guess_word(guess: str, current_word: str):
    guess = guess.lower()
    current_word = current_word.lower()

    result = ["⬛"] * 5
    remaining_letters = list(current_word)
    letter_updates = {}

    # 🟩 First pass (greens)
    for i in range(5):
        if guess[i] == current_word[i]:
            result[i] = "🟩"
            remaining_letters[i] = ""
            letter_updates[guess[i]] = "correct"

    # 🟨 Second pass (yellows)
    for i in range(5):
        if result[i] == "🟩":
            continue

        if guess[i] in remaining_letters:
            result[i] = "🟨"
            remaining_letters[remaining_letters.index(guess[i])] = ""

            if letter_updates.get(guess[i]) != "correct":
                letter_updates[guess[i]] = "present"
        else:
            if guess[i] not in letter_updates:
                letter_updates[guess[i]] = "wrong"

    return " ".join(result), letter_updates


def upload_words(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]

    for word in words:
        db.collection("words").document(word).set({"status": "available"})


def mark_word_used(word: str):
    db.collection("words").document(word).update({"status": "used"})


def get_wordle_word():
    words_ref = db.collection("words")
    docs = words_ref.where("status", "==", "current").stream()
    doc = next(docs, None)

    if doc is None:
        return None

    wordle_word = doc.id
    return wordle_word


def choose_new_word():
    words_ref = db.collection("words")

    current_docs = words_ref.where("status", "==", "current").stream()

    for doc in current_docs:
        doc.reference.update({"status": "used"})

    available_docs = list(words_ref.where("status", "==", "available").stream())

    if not available_docs:
        return None
    selected = random.choice(available_docs)

    selected.reference.update({"status": "current"})

    return selected.id
