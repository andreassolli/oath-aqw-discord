from typing import Literal

import discord
from discord import app_commands
from discord.abc import Messageable
from discord.ext import commands
from google.cloud import firestore
from google.cloud.firestore import ArrayUnion

from config import (
    ADMIN_ROLE_ID,
    ALLOWED_COMMANDS_CHANNELS,
    BETA_TESTER_ROLE_ID,
    BETA_TESTING_CHANNEL_ID,
    BOT_GUY_ROLE_ID,
    DISCORD_MANAGER_ROLE_ID,
    INITIATE_ROLE_ID,
    OATHSWORN_ROLE_ID,
    OFFICER_ROLE_ID,
    TICKET_LOG_CHANNEL_ID,
)
from economy.gamba.coinflip import run_coinflip
from economy.gamba.doom_view import DoomSpinView
from economy.gamba.utils import has_spun_today
from economy.gamba.yanken_accept_view import RPSAcceptView
from extra_commands.memes import (
    m_bigrig,
    m_dryage,
    m_gld,
    m_goon_greed,
    m_juns,
    m_mapril,
    m_oath,
    m_og_pro,
    m_og_san,
    m_rcs,
    m_sker,
    m_yokai,
)
from extra_commands.utils import (
    check_missing_badges,
    elect_potw,
    has_any_role,
    manual_leaderboard_post,
    send_winner_embed,
)
from extra_commands.wordle import (
    ShareWordleView,
    choose_new_word,
    get_wordle_word,
    guess_word,
)
from extra_commands.wordle_image import generate_wordle_board
from firebase_client import db


class Extra(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="aqwordle", description="Todays AQW Wordle")
    @app_commands.describe(guess="Your guess for today's Wordle")
    async def wordle(self, interaction: discord.Interaction, guess: str | None = None):

        await interaction.response.defer(ephemeral=True)

        wordle_word = get_wordle_word()
        if wordle_word is None:
            await interaction.followup.send("❌ No wordle word found.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        game_ref = db.collection("wordle_games").document(user_id)

        doc = game_ref.get()
        data = doc.to_dict() if doc.exists else {}
        guess = guess.strip().lower() if guess else None

        saved_word = data.get("current_word")
        completed = data.get("completed", False)
        letter_states = data.get("letter_states", {})
        was_completed = data.get("completed", False)
        if completed and saved_word == wordle_word and guess:
            guesses = data.get("guesses", [])
            guess_count = data.get("guess_count", 0)
            won = data.get("won", False)

            board_image = await generate_wordle_board(interaction)
            file = discord.File(board_image, filename="wordle.png")

            if won:
                view = ShareWordleView(guess_count)
                await interaction.followup.send(
                    content=f"✅ You've already completed today's AQWordle in {guess_count}/6 guesses.",
                    file=file,
                    view=view,
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    content=f"❌ You did not manage to complete today's Wordle. The word was **{wordle_word}**.",
                    file=file,
                    ephemeral=True,
                )

            return

        if not guess:
            board_image = await generate_wordle_board(interaction)
            file = discord.File(board_image, filename="wordle.png")

            guess_count = data.get("guess_count", 0)

            if completed and saved_word == wordle_word:
                return await interaction.followup.send(
                    content=f"✅ You completed today's AQWordle in {guess_count}/6 guesses.",
                    file=file,
                    ephemeral=True,
                    view=ShareWordleView(guess_count),
                )
            else:
                return await interaction.followup.send(
                    content=f"📊 **Current AQWordle progress — {guess_count}/6 guesses used**",
                    file=file,
                    ephemeral=True,
                )

        # If new word OR no existing data → reset progress
        if saved_word != wordle_word:
            guesses = []
            guess_count = 0
            letter_states = dict()
        else:
            guesses = data.get("guesses", [])
            guess_count = data.get("guess_count", 0)
            letter_states = data.get("letter_states", {})

        words_completed = data.get("words_completed", 0)

        if len(guess) != 5:
            await interaction.followup.send(
                "❌ Your guess must be 5 letters long.", ephemeral=True
            )
            return
        result, letter_updates = guess_word(guess, wordle_word)
        guesses.append(
            {
                "pattern": result,  # "🟩 🟨 ⬛ ⬛ 🟩"
                "guess": guess.lower(),
            }
        )
        guess_count += 1
        correct = guess.lower() == wordle_word.lower()
        if correct:
            words_completed += 1

        for letter, state in letter_updates.items():
            existing = letter_states.get(letter)

            # Priority: correct > present > wrong
            if existing == "correct":
                continue
            if existing == "present" and state == "wrong":
                continue
            if existing == "wrong" and state in ("present", "correct"):
                letter_states[letter] = state
            else:
                letter_states[letter] = state

        game_ref.set(
            {
                "guesses": guesses,
                "guess_count": guess_count,
                "words_completed": words_completed,
                "current_word": wordle_word,
                "completed": correct or guess_count >= 6,
                "won": correct,
                "letter_states": letter_states,
            }
        )
        view = None
        board_image = await generate_wordle_board(interaction)
        file = discord.File(board_image, filename="wordle.png")

        if not correct and guess_count >= 6:
            await interaction.followup.send(
                content=f"❌ You did not manage to complete today's Wordle. The word was **{wordle_word}**.",
                file=file,
                ephemeral=True,
            )
            return

        if correct and not was_completed:
            db.collection("users").document(str(user_id)).update(
                {"coins": firestore.Increment(750)}
            )

        if correct:
            view = ShareWordleView(guess_count)
            await interaction.followup.send(
                content="🎉 You have completed today's Wordle and got <:oathcoin:1462999179998531614> 750!",
                file=file,
                view=view,
                ephemeral=True,
            )
            return

        await interaction.followup.send(file=file, ephemeral=True)

    @app_commands.command(name="badge-check", description="Check missing badges")
    async def badge_check(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ):
        await interaction.response.defer()
        if interaction.channel_id not in ALLOWED_COMMANDS_CHANNELS:
            allowed_mentions = ", ".join(
                f"<#{cid}>" for cid in ALLOWED_COMMANDS_CHANNELS
            )

            await interaction.followup.send(
                f"❌ This command can only be used in {allowed_mentions}.",
                ephemeral=True,
            )
            return
        guild = interaction.guild
        if not guild:
            await interaction.followup.send(
                f"❌ Guild not found.",
                ephemeral=True,
            )
            return
        member = user if user else guild.get_member(interaction.user.id)
        if not member:
            await interaction.followup.send(
                f"❌ User not found.",
                ephemeral=True,
            )
            return
        embed = await check_missing_badges(member)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="og-san")
    async def og_san(self, interaction: discord.Interaction):
        await m_og_san(interaction)

    @app_commands.command(name="juns")
    async def juns(self, interaction: discord.Interaction):
        await m_juns(interaction)

    @app_commands.command(name="elect-potw", description="Elect a player for POTW")
    @app_commands.checks.has_role(DISCORD_MANAGER_ROLE_ID)
    async def elect_potw(
        self, interaction: discord.Interaction, player: discord.Member
    ):
        await elect_potw(player)
        await interaction.response.send_message(
            f"🎉 {player.mention} has been elected POTW!"
        )

    @app_commands.command(name="nominate", description="Nominate a player for POTW")
    @app_commands.checks.has_role(OATHSWORN_ROLE_ID)
    async def nominate(self, interaction: discord.Interaction, player: discord.Member):
        is_oath_member = any(role.id == INITIATE_ROLE_ID for role in player.roles)
        if not is_oath_member:
            await interaction.response.send_message(
                f"{player.mention} is not in Oath Guild and cannot be nominated for POTW."
            )
            return

        db.collection("meta").document("potw_nominees").update(
            {"nominees": ArrayUnion([str(player.id)])}
        )

        await interaction.response.send_message(
            f"{player.mention} has been nominated for POTW!"
        )

    @app_commands.command(name="elp", description="Call for ELP")
    async def elp(self, interaction: discord.Interaction):
        await interaction.response.send_message("ELP ELLPPPPP CALL DRIADGEEEEEEEEEEEE")

    @app_commands.command(name="oath", description="Call for Oath")
    async def oath(self, interaction: discord.Interaction):
        await m_oath(interaction)

    @app_commands.command(name="dryage")
    async def dryage(self, interaction: discord.Interaction):
        await m_dryage(interaction)

    @app_commands.command(name="movie")
    async def movie(self, interaction: discord.Interaction):
        message = "Producers it's time for Movies! People are trying to do Gramiel or Speaker with their feet, come to VC!"
        await interaction.response.send_message(message)

    @app_commands.command(name="rcs")
    async def anime(self, interaction: discord.Interaction):
        await m_rcs(interaction)

    @app_commands.command(name="sker")
    async def sker_ready(self, interaction: discord.Interaction):
        await m_sker(interaction)

    @app_commands.command(name="ecr")
    async def ecr(self, interaction: discord.Interaction):
        message = """East Coast Roster:\n
    Driadge - Pot Scammer Granny Slammer\n
    SCR - Voted most likely to be kidnapped in highschool\n
    Veritus - King of the self-dox\n
    Killer - Pay2Lose Enjoyer might enact slave labor and torture friends"""
        await interaction.response.send_message(message)

    @app_commands.command(name="bigrig", nsfw=True)
    @has_any_role(ADMIN_ROLE_ID, DISCORD_MANAGER_ROLE_ID)
    async def bigrig(self, interaction: discord.Interaction):
        await m_bigrig(interaction)

    @app_commands.command(name="mapril")
    async def mapril(self, interaction: discord.Interaction):
        await m_mapril(interaction)

    @app_commands.command(name="greed")
    async def greed(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Is this mapril using this command? <a:mapGiggle:1478032348401373326>"
        )

    @app_commands.command(name="gld")
    @has_any_role(ADMIN_ROLE_ID, DISCORD_MANAGER_ROLE_ID)
    async def glad(self, interaction: discord.Interaction):
        await m_gld(interaction)

    @app_commands.command(name="goon-greed")
    async def goon_greed(self, interaction: discord.Interaction):
        await m_goon_greed(interaction)

    @app_commands.command(name="og-pro")
    async def og_pro(self, interaction: discord.Interaction):
        await m_og_pro(interaction)

    @app_commands.command(name="yokai")
    async def yokai(self, interaction: discord.Interaction):
        await m_yokai(interaction)

    @app_commands.command(name="announce-event-winner")
    @has_any_role(ADMIN_ROLE_ID, DISCORD_MANAGER_ROLE_ID)
    async def announce_event_winner(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        title: str,
        message: str,
        where: Literal["All", "Oath"],
    ):
        await send_winner_embed(interaction, user, title, message, where)

    @app_commands.command(name="manual-leaderboard-post")
    @app_commands.checks.has_role(BOT_GUY_ROLE_ID)
    async def manual_leaderboard_post_command(self, interaction: discord.Interaction):
        await manual_leaderboard_post(interaction)

    @app_commands.command(
        name="ioda-list",
        description="Get the link to the IoDA spreadsheet",
    )
    async def ioda_list(self, interaction):
        return await interaction.response.send_message(
            "https://docs.google.com/document/d/1T4fut_U8Wptopw0coWCU29WCK5arAtGBy5lzlDpwswE/edit?tab=t.0"
        )

    @app_commands.command(
        name="say",
        description="Make the bot say something in current location",
    )
    @app_commands.checks.has_role(BOT_GUY_ROLE_ID)
    async def say(self, interaction: discord.Interaction, message: str):

        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel

        if not isinstance(channel, Messageable):
            return

        await channel.send(content=message)

    @app_commands.command(name="warn", description="Warn a user who oversteps")
    @app_commands.checks.has_role(OFFICER_ROLE_ID)
    async def warn(
        self, interaction: discord.Interaction, user: discord.User, message: str
    ):
        guild = interaction.guild
        moderator = interaction.user
        dm = await user.create_dm()
        embed = discord.Embed(title="Warning", description=message)
        await dm.send(embed=embed)
        if not guild:
            return
        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        log_embed = discord.Embed(
            title=f"Warning issued for {user.display_name} ({user.mention}), issued by {moderator.display_name} ({moderator.mention})",
            description=message,
            color=discord.Color.red(),
        )
        if not isinstance(log_channel, discord.TextChannel):
            return
        await log_channel.send(embed=log_embed)
        return await interaction.followup.send(f"Warned {user.mention}", ephemeral=True)

    @app_commands.command(
        name="new-aqwordle",
        description="Select new AQWordle word",
    )
    @app_commands.checks.has_role(BOT_GUY_ROLE_ID)
    async def new_aqwordle(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        choose_new_word()

        return await interaction.followup.send("New AQWordle word selected")


async def setup(bot: commands.Bot):
    await bot.add_cog(Extra(bot))
