from firebase_client import db

DEFAULT_POINTS = 1
_rule_cache = None


def load_point_rules():
    global _rule_cache
    if _rule_cache is None:
        _rule_cache = []
        for doc in db.collection("point_rules").stream():
            data = doc.to_dict() or {}
            data["id"] = doc.id
            _rule_cache.append(data)
    return _rule_cache


def clear_point_rule_cache():
    global _rule_cache
    _rule_cache = None


def calculate_ticket_points(note: str) -> int:
    if not note:
        return DEFAULT_POINTS

    note_lower = note.lower()
    rules = load_point_rules()

    for rule in rules:
        if rule["id"].lower() in note_lower:
            return int(rule.get("points", DEFAULT_POINTS))

    return DEFAULT_POINTS


DEFAULT_ROOM = ""
_rooms_cache = None


def load_boss_rooms():
    global _rooms_cache
    if _rooms_cache is None:
        _rooms_cache = []
        for doc in db.collection("point_rules").stream():
            data = doc.to_dict() or {}
            data["id"] = doc.id
            _rooms_cache.append(data)
    return _rooms_cache


def clear_boss_room_cache():
    global _rooms_cache
    _rooms_cache = None


def get_boss_room(boss: str) -> str:
    if not boss:
        return DEFAULT_ROOM

    boss_lower = boss.lower()
    rooms = load_boss_rooms()

    for room in rooms:
        if room["id"].lower() == boss_lower:
            return room.get("room", DEFAULT_ROOM)

    return DEFAULT_ROOM
