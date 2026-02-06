from firebase_client import db

def get_type_choices():
    types = []
    for doc in db.collection("bosses").stream():
        data = doc.to_dict()
        types.append({
            "id": doc.id,
        })
    return types
