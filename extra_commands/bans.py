from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import uses_relative

from firebase_admin import firestore

from firebase_client import db
from user_verification.utils import fetch_aqw_profile

BANS_COLLECTION = "bans"


def get_all_bans() -> List[Dict[str, Any]]:
    docs = db.collection(BANS_COLLECTION).stream()
    return [{"username": doc.id, **(doc.to_dict() or {})} for doc in docs]


async def is_user_banned(username: str):
    user = await fetch_aqw_profile(username)
    if not user:
        return None
    ccid = user["ccid"] if user["ccid"] else username.lower()

    query = db.collection(BANS_COLLECTION).where("ccid", "==", ccid).limit(1).get()
    docs = list(query)

    if not docs:
        return None

    return docs[0]


# ➕ Add ban
async def add_ban(
    *,
    discord_id: int | None,
    username: str,
    reason: str,
    banned_by: int,
) -> None:
    user = await fetch_aqw_profile(username)
    if not user:
        user = {}
    ccid = user["ccid"] if user["ccid"] else username.lower()
    db.collection(BANS_COLLECTION).document(ccid).set(
        {
            "username": username,
            "discord_id": discord_id,
            "reason": reason,
            "banned_by": banned_by,
            "ccid": ccid,
            "banned_at": firestore.SERVER_TIMESTAMP,
        }
    )


async def remove_ban(username: str) -> bool:
    doc = await is_user_banned(username)

    if not doc:
        return False

    doc.reference.delete()
    return True
