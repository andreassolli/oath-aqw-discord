from google.cloud import firestore

from firebase_client import db


async def process_count_message(message):
    state_ref = db.collection("meta").document("counting")
    state_doc = state_ref.get()
    state = state_doc.to_dict() if state_doc.exists else {}

    last_number = state.get("last_number", 0)
    last_user = state.get("last_user")

    # ❌ Not a number
    if not message.content.isdigit():
        return False

    number = int(message.content)

    # ❌ Wrong number
    if number != last_number + 1:
        return False

    # ❌ Same user twice
    if last_user == message.author.id:
        return False

    state_ref.set(
        {
            "last_number": number,
            "last_user": message.author.id,
        },
        merge=True,
    )

    db.collection("users").document(str(message.author.id)).set(
        {
            "counting_score": firestore.Increment(1),
        },
        merge=True,
    )

    return True
