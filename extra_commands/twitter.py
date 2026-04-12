import asyncio
import json

import aiohttp
import feedparser
import requests
from discord.ext import tasks
from tweepy import Client as TwitterClient

from config import (
    INITIATE_ROLE_ID,
    NEWS_WEBHOOK_URL,
    OATH_USER_ID,
    TWITTER_BEARER_TOKEN,
)
from firebase_client import db


def load_last_id():
    doc = db.collection("tweets").document("last").get()
    if doc.exists:
        return doc.to_dict().get("id")
    return None


def save_last_id(entry_id):
    db.collection("tweets").document("last").set({"id": entry_id})


def get_latest_entry():
    client = TwitterClient(bearer_token=TWITTER_BEARER_TOKEN)

    response = client.get_users_tweets(
        id=OATH_USER_ID,
        max_results=5,
        tweet_fields=["created_at", "attachments"],
        expansions=["attachments.media_keys"],
        media_fields=["url", "preview_image_url"],
    )

    if not response.data:
        return None, None

    tweet = response.data[0]

    media_url = None

    if hasattr(tweet, "attachments") and tweet.attachments:
        media_keys = tweet.attachments.get("media_keys", [])

        if response.includes and "media" in response.includes:
            media_lookup = {m.media_key: m for m in response.includes["media"]}

            for key in media_keys:
                media = media_lookup.get(key)
                if media:
                    media_url = media.url or media.preview_image_url
                    break  # take first image only

    return tweet, media_url


@tasks.loop(seconds=120)
async def check_twitter():

    try:
        entry, image_url = get_latest_entry()

        last_entry_id = load_last_id()

        if entry and str(entry.id) != str(last_entry_id):
            tweet_link = f"https://twitter.com/{OATH_USER_ID}/status/{entry.id}"
            tweet_text = entry.text

            await send_to_discord(tweet_text, tweet_link, image_url)
            save_last_id(str(entry.id))
    except Exception as e:
        import traceback

        traceback.print_exc()


async def send_to_discord(text, link, image_url=None):
    role_mention = f"<@&{INITIATE_ROLE_ID}>"

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
            if image_url:
                embed["image"] = {"url": image_url}
                await session.post(NEWS_WEBHOOK_URL, json=data)

            else:
                with open("assets/oath-logo.png", "rb") as f:
                    embed["image"] = {"url": "attachment://oath-logo.png"}

                    form = aiohttp.FormData()
                    form.add_field(
                        "payload_json",
                        json.dumps(data),
                        content_type="application/json",
                    )
                    form.add_field("file", f, filename="oath-logo.png")

                    await session.post(NEWS_WEBHOOK_URL, data=form)
