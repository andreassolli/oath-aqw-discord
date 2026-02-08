import re

from firebase_client import db

DEFAULT_POINTS = 1
_RULE_CACHE = None


def load_point_rules():
    global _RULE_CACHE
    if _RULE_CACHE is None:
        _RULE_CACHE = [rule.to_dict() for rule in db.collection("point_rules").stream()]
    return _RULE_CACHE


def clear_point_rule_cache():
    global _RULE_CACHE
    _RULE_CACHE = None


def calculate_ticket_points(note: str) -> int:
    if not note:
        return DEFAULT_POINTS

    note_lower = note.lower()

    for doc in db.collection("point_rules").stream():
        if doc.id.lower() in note_lower:
            return int(doc.to_dict().get("points", DEFAULT_POINTS))

    return DEFAULT_POINTS


DEFAULT_ROOM = ""
_ROOMS_CACHE = None


def load_boss_rooms():
    global _ROOMS_CACHE
    if _ROOMS_CACHE is None:
        _ROOMS_CACHE = [
            boss_room.to_dict() for boss_room in db.collection("point_rules").stream()
        ]
    return _ROOMS_CACHE


def clear_boss_room_cache():
    global _ROOMS_CACHE
    _ROOMS_CACHE = None


def get_boss_room(boss: str) -> str:
    if not boss:
        return DEFAULT_ROOM

    boss_lower = boss.lower()

    for doc in db.collection("point_rules").stream():
        if doc.id.lower() == boss_lower:
            return doc.to_dict().get("room", DEFAULT_ROOM)

    return DEFAULT_ROOM
