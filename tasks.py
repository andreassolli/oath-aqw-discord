import asyncio
from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from config import OFFICER_CHANNEL_ID
from extra_commands.utils import create_potw_poll, elect_potw_by_name
from firebase_client import db

EST = ZoneInfo("America/New_York")

bot_instance = None


def setup_tasks(bot):
    global bot_instance
    bot_instance = bot

    # potw_nomination_reminder.start()
    # weekly_potw_poll.start()
    # check_expired_polls.start()


@tasks.loop(minutes=5)
async def check_expired_polls():
    doc = db.collection("meta").document("potw_poll").get()
    if not doc.exists:
        return

    data = doc.to_dict()
    ends_at = data["ends_at"]

    if datetime.now(UTC) < ends_at:
        return

    channel = bot_instance.get_channel(data["channel_id"])
    if not channel:
        return

    try:
        message = await channel.fetch_message(data["message_id"])
    except discord.NotFound:
        return

    poll = message.poll

    if not poll:
        return

    winner_answer = poll.victor_answer

    if not winner_answer:
        return

    winner_name = winner_answer.text

    if winner_name:
        await elect_potw_by_name(winner_answer, channel.guild)
        await db.collection("meta").document("potw_nominees").update({"nominees": []})

    # delete poll doc so it doesn't run again
    db.collection("meta").document("potw_poll").delete()


#
# SATURDAY 5 PM EST → reminder
#
@tasks.loop(time=time(hour=17, minute=0, tzinfo=EST))
async def potw_nomination_reminder():

    # Only run Saturday
    now_est = datetime.now(EST)

    if now_est.weekday() != 5:  # 5 = Saturday
        return

    channel = bot_instance.get_channel(OFFICER_CHANNEL_ID)

    if channel:
        await channel.send(
            "📢 **Reminder:** Nominate players for Player of the Week!\n\n"
            "Poll opens tomorrow at 5 PM EST."
        )


#
# SUNDAY 5 PM EST → create poll
#
@tasks.loop(time=time(hour=17, minute=0, tzinfo=EST))
async def weekly_potw_poll():
    now_est = datetime.now(EST)

    if now_est.weekday() != 6:
        return

    channel = bot_instance.get_channel(OFFICER_CHANNEL_ID)

    if not channel:
        return

    message = await create_potw_poll(channel)
    if not message:
        return
    # Schedule election exactly 24h later
    asyncio.create_task(
        schedule_election(
            message.id,
            channel.id,
            datetime.now(UTC) + timedelta(days=1),
        )
    )


async def schedule_election(message_id, channel_id, run_at):

    delay = (run_at - datetime.now(UTC)).total_seconds()

    if delay > 0:
        await asyncio.sleep(delay)

    channel = bot_instance.get_channel(channel_id)

    if not channel:
        return

    try:
        message = await channel.fetch_message(message_id)
    except discord.NotFound:
        return

    poll = message.poll

    if not poll:
        return

    winner_answer = poll.victor_answer

    if not winner_answer:
        return

    winner_name = winner_answer.text

    if winner_name:
        await elect_potw_by_name(winner_name, channel.guild)

        await db.collection("meta").document("potw_nominees").update({"nominees": []})

        await channel.send(f"🧹 Nominees list has been reset for next week.")


@potw_nomination_reminder.before_loop
async def before_nomination():
    await bot_instance.wait_until_ready()


@weekly_potw_poll.before_loop
async def before_weekly():
    await bot_instance.wait_until_ready()


@check_expired_polls.before_loop
async def before_check():
    await bot_instance.wait_until_ready()
