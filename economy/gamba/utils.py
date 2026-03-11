import random
from datetime import datetime, timezone

from firebase_client import db


async def coinflip(fair: bool = False, heads: bool = True) -> str:
    toss = random.randint(1, 100)
    if fair:
        return "Heads" if toss <= 50 else "Tails"
    else:
        if heads:
            return "Heads" if toss <= 49 else "Tails"
        else:
            return "Tails" if toss <= 49 else "Heads"


async def has_spun_today(user_id: int) -> bool:
    doc = db.collection("users").document(str(user_id)).get()

    if not doc.exists:
        return False

    last_spin = doc.to_dict().get("last_spin")
    if not last_spin:
        return False

    now = datetime.now(timezone.utc)

    return last_spin.date() == now.date()


async def set_spin_today(user_id: int):
    db.collection("users").document(str(user_id)).set(
        {"last_spin": datetime.now(timezone.utc)}, merge=True
    )
