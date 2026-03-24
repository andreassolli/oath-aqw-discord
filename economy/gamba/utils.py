import random
from datetime import datetime, timedelta, timezone

from google.cloud.firestore import Increment

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


async def has_spun_today(user_id: int) -> tuple[bool, timedelta | None]:
    doc = db.collection("users").document(str(user_id)).get()

    if not doc.exists:
        return False, None

    last_spin = doc.to_dict().get("last_spin")
    if not last_spin:
        return False, None

    now = datetime.now(timezone.utc)

    # next reset = next midnight UTC
    next_reset = datetime.combine(
        now.date() + timedelta(days=1),
        datetime.min.time(),
        tzinfo=timezone.utc,
    )

    if last_spin.date() == now.date():
        remaining = next_reset - now
        return True, remaining

    return False, None


async def set_spin_today(user_id: int):
    db.collection("users").document(str(user_id)).set(
        {"last_spin": datetime.now(timezone.utc)}, merge=True
    )


def lock_coins(user_id: int, amount: int) -> tuple[bool, str | None]:
    user_ref = db.collection("users").document(str(user_id))

    doc = user_ref.get()
    data = doc.to_dict() or {}

    coins = data.get("coins", 0)
    locked = data.get("locked_coins", 0)

    available = coins - locked

    if available < amount:
        return False, "Not enough available coins."

    user_ref.update({"locked_coins": Increment(amount)})

    return True, None


def unlock_coins(user_id: int, amount: int):

    user_ref = db.collection("users").document(str(user_id))

    user_ref.update({"locked_coins": Increment(-amount)})


def format_time(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    return f"{hours}h {minutes}m"
