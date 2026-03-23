import random

from firebase_client import firestore


def reward_gems_if_needed(user_ref, user_data, points_added: int):
    current_points = user_data.get("points", 0)
    last_rewarded = user_data.get("gems_awarded_points", 0)

    new_total = current_points + points_added
    new_chunks = (new_total - last_rewarded) // 15

    if new_chunks <= 0:
        return

    gems_to_add = sum(random.randint(1, 3) for _ in range(new_chunks))

    user_ref.update(
        {
            "gems": firestore.Increment(gems_to_add),
            "gems_awarded_points": last_rewarded + (new_chunks * 15),
        }
    )
