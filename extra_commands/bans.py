from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import uses_relative
from google.cloud.firestore_v1 import FieldFilter, Or
from firebase_admin import firestore

from firebase_client import db
from user_verification.utils import fetch_aqw_profile

BANS_COLLECTION = "bans"


def get_all_bans() -> List[Dict[str, Any]]:
    docs = db.collection(BANS_COLLECTION).stream()
    bans = [{"username": doc.id, **(doc.to_dict() or {})} for doc in docs]

    bans.sort(
        key=lambda b: b.get("banned_at") or datetime.min,
        reverse=True,
    )
    return bans


async def is_user_banned(username: str):
    user = await fetch_aqw_profile(username)
    ccid = user["ccid"] if user else "-1"

    query = (
        db.collection(BANS_COLLECTION)
        .where(
            filter=Or([
                FieldFilter("ccid", "==", ccid),
                FieldFilter("username", "==", username.lower()),
            ])
        )
        .limit(5)
    ).get()

    if not query:
        return None

    return [doc.to_dict() for doc in query]


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
