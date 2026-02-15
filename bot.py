import logging
import os

import discord
from discord.ext import commands

from config import APPLICATION_ID
from startup import run_startup_tasks

logging.basicConfig(level=logging.INFO)

_synced = False

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("/"),
    intents=intents,
    application_id=APPLICATION_ID,
)


@bot.event
async def on_ready():
    global _synced

    if not _synced:
        await bot.tree.sync()
        _synced = True

    await run_startup_tasks(bot)

    if bot.user:
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")


async def main():
    async with bot:
        for ext in (
            "cogs.profile",
            "cogs.tickets",
            "cogs.admin",
            "cogs.verification",
            "cogs.classes",
            "cogs.bans",
            "cogs.extra",
        ):
            await bot.load_extension(ext)
        await bot.start(os.environ["DISCORD_TOKEN"])


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
