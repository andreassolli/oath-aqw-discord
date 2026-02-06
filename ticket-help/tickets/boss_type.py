from firebase_client import db

def get_bosses_for_type(ticket_type: str) -> list[str]:
    doc = db.collection("bosses").document(ticket_type).get()
    if not doc.exists:
        return []

    data = doc.to_dict() or {}
    return data.get("bosses", [])
