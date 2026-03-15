import asyncio

import aiohttp

from economy.shop_generation import generate_shop
from extra_commands.wordle import choose_new_word
from extra_commands.wordle_share import generate_wordle_share
from firebase_client import db
from request_utils import get_session
from user_profile.utils import fetch_inventory
from user_verification.utils import fetch_aqw_profile

BANS_COLLECTION = "bans"


async def backfill_ccids():
    docs = db.collection(BANS_COLLECTION).stream()

    updated = 0

    for doc in docs:
        data = doc.to_dict() or {}

        # Skip if ccid already exists
        if "ccid" in data and data["ccid"] == data["username"]:
            print(data["ccid"])
            continue

    print(f"\nFinished. Updated {updated} documents.")


def get_all_users():
    docs = db.collection("users").stream()

    sorted_users = []

    for doc in docs:
        data = doc.to_dict() or {}
        ccid = data.get("ccid")

        if ccid:
            sorted_users.append(
                {"ccid": int(ccid), "username": data.get("aqw_username")}
            )

    sorted_users.sort(key=lambda x: x["ccid"])
    print(sorted_users)


if __name__ == "__main__":
    # get_all_users()
    # choose_new_word()
    asyncio.run(generate_shop())
    # asyncio.run(backfill_ccids())
    # asyncio.run(generate_wordle_share(None, "292040660696039424"))
