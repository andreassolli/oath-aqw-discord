from datetime import datetime
from typing import Any, Dict, List, Optional

from firebase_admin import firestore

from firebase_client import db

BANS_COLLECTION = "bans"


def get_all_bans() -> List[Dict[str, Any]]:
    docs = db.collection(BANS_COLLECTION).stream()
    return [{"username": doc.id, **(doc.to_dict() or {})} for doc in docs]


def is_user_banned(username: str) -> Optional[Dict[str, Any]]:
    doc = db.collection(BANS_COLLECTION).document(username).get()
    if not doc.exists:
        return None
    return doc.to_dict()


# ➕ Add ban
def add_ban(
    *,
    discord_id: int | None,
    username: str,
    reason: str,
    banned_by: int,
) -> None:
    db.collection(BANS_COLLECTION).document(username).set(
        {
            "username": username,
            "discord_id": discord_id,
            "reason": reason,
            "banned_by": banned_by,
            "banned_at": firestore.SERVER_TIMESTAMP,
        }
    )


def remove_ban(username: str) -> bool:
    doc_ref = db.collection(BANS_COLLECTION).document(username)
    doc = doc_ref.get()

    if not doc.exists:
        return False

    doc_ref.delete()
    return True
