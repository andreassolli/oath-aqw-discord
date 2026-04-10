import asyncio

import aiohttp
import feedparser
import requests
from discord.ext import tasks

from config import INITIATE_ROLE_ID, NEWS_WEBHOOK_URL
from firebase_client import db

RSS_URL = "https://rss.app/feeds/fJjHnQTQN43lL4Ot.xml"


def load_last_id():
    doc = db.collection("tweets").document("last").get()
    if doc.exists:
        return doc.to_dict().get("id")
    return None


def save_last_id(entry_id):
    db.collection("tweets").document("last").set({"id": entry_id})


def get_latest_entry():
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        return None

    return feed.entries[0]


@tasks.loop(seconds=60)
async def check_rss():
    try:
        entry = get_latest_entry()
        last_entry_id = load_last_id()

        if entry and entry.id != last_entry_id:
            save_last_id(entry.id)

            tweet_link = entry.link
            tweet_text = entry.title
            image_url = get_image_from_entry(entry)

            await send_to_discord(tweet_text, tweet_link, image_url)

    except Exception as e:
        print("Error:", e)


async def send_to_discord(text, link, image_url=None):
    # role_mention = f"<@&{INITIATE_ROLE_ID}>"
    role_mention = f""

    embed = {
        "title": "🐦 New Tweet from Oath!",
        "description": text,
        "url": link,
        "color": 0x1DA1F2,
    }

    if image_url:
        embed["image"] = {"url": image_url}

    data = {
        "content": role_mention,
        "embeds": [embed],
        "allowed_mentions": {"parse": ["roles"]},
    }
    if NEWS_WEBHOOK_URL:
        async with aiohttp.ClientSession() as session:
            await session.post(NEWS_WEBHOOK_URL, json=data)


def get_image_from_entry(entry):

    if hasattr(entry, "media_content"):
        media = entry.media_content
        if media and "url" in media[0]:
            return media[0]["url"]

    if hasattr(entry, "enclosures"):
        if entry.enclosures:
            return entry.enclosures[0].get("href")

    if "summary" in entry:
        import re

        match = re.search(r'<img.*?src="(.*?)"', entry.summary)
        if match:
            return match.group(1)

    return None
