import random

import discord
from google.cloud import firestore

from firebase_client import db


async def process_count_message(message):
    state_ref = db.collection("meta").document("counting")
    state_doc = state_ref.get()
    state = state_doc.to_dict() if state_doc.exists else {}
    recent_users = state.get("recent_users", [])
    last_number = state.get("last_number", 0)
    last_user = state.get("last_user")

    if not message.content.isdigit():
        return False

    number = int(message.content)

    if number != last_number + 1:
        return False

    if last_user == str(message.author.id):
        return False

    user_id = str(message.author.id)

    recent_users.append(user_id)

    recent_users = recent_users[-10:]
    state_ref.set(
        {
            "last_number": number,
            "last_user": str(message.author.id),
            "recent_users": recent_users,
        },
        merge=True,
    )
    if number % 100 == 0 and len(recent_users) > 0:
        total_reward = 200
        rewarded_users = set(recent_users)
        split = total_reward // len(rewarded_users)

        for uid in rewarded_users:
            db.collection("users").document(uid).set(
                {
                    "coins": firestore.Increment(split),
                },
                merge=True,
            )

        mentions = " ".join(f"<@{uid}>" for uid in rewarded_users)

        embed = discord.Embed(
            title="💰 Global Milestone!",
            description=(
                f"🎉 We reached **{number}**!\n\n"
                f"The last contributors {mentions}\n"
                f"each receive **<:oathcoin:1462999179998531614>{split}!**"
            ),
            color=discord.Color.green(),
        )

        await message.channel.send(embed=embed)

    user_ref = db.collection("users").document(str(message.author.id))

    user_ref.set(
        {
            "counting_score": firestore.Increment(1),
        },
        merge=True,
    )

    user_doc = user_ref.get()
    user_data = user_doc.to_dict() or {}
    score = user_data.get("counting_score", 0)

    if score % 10 == 0:
        coins = random.randint(20, 30)

        user_ref.set(
            {
                "coins": firestore.Increment(coins),
            },
            merge=True,
        )

        embed = discord.Embed(
            title="🎉 Checkpoint reached!",
            description=(
                f"{message.author.mention} has counted **{score}** times, "
                f"and received **<:oathcoin:1462999179998531614>{coins}!**"
            ),
            color=discord.Color.gold(),
        )

        await message.channel.send(embed=embed)

    return True
