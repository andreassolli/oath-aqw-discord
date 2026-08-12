from firebase_client import db
import json

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

INPUT_FILE = "spam_bosses.json"
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    SPAM_BOSSES = json.load(f)

def get_spam_boss_room(boss:str) -> dict:
    for spam_boss in SPAM_BOSSES:
        if boss == spam_boss["name"]:
            return({"room": spam_boss["room"], "players": spam_boss["max_players"]-1})
    return {}

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
