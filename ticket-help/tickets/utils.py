from firebase_client import db
from firebase_admin import firestore
from typing import Optional
from datetime import datetime, timedelta

def get_week_start(dt: datetime):
    # Monday start (ISO week)
    return dt - timedelta(days=dt.weekday())


def set_active_ticket(user_id: int, ticket_name: str):
    user_ref = db.collection("users").document(str(user_id))
    user_ref.set(
        {"active_ticket": ticket_name},
        merge=True
    )

def clear_active_ticket(user_id: int, ticket_name: Optional[str] = None):

    user_ref = db.collection("users").document(str(user_id))
    doc = user_ref.get()

    if not doc.exists:
        return

    data = doc.to_dict() or {}

    if ticket_name is None or data.get("active_ticket") == ticket_name:
        user_ref.update({
            "active_ticket": firestore.DELETE_FIELD
        })
