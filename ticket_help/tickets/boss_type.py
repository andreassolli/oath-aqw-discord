from firebase_client import db

from .points import get_boss_room  # import from points.py


def get_bosses_for_type(ticket_type: str) -> list[dict[str, str]]:
    doc = db.collection("bosses").document(ticket_type).get()
    if not doc.exists:
        return []

    data = doc.to_dict() or {}
    bosses = data.get("bosses", [])

    results = []

    for boss in bosses:
        room = get_boss_room(boss)
        results.append(
            {
                "name": boss,
                "room": room,
            }
        )

    return results
