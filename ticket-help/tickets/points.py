import re
from firebase_client import db

DEFAULT_POINTS = 1
_RULE_CACHE = None

def load_point_rules():
    global _RULE_CACHE
    if _RULE_CACHE is None:
        _RULE_CACHE = [
            rule.to_dict()
            for rule in db.collection("point_rules").stream()
        ]
    return _RULE_CACHE

def clear_point_rule_cache():
    global _RULE_CACHE
    _RULE_CACHE = None

def calculate_ticket_points(note: str) -> int:
    if not note:
        return DEFAULT_POINTS

    note = note.lower()

    for rule in load_point_rules():
        for keyword in rule.get("keywords", []):
            pattern = rf"\b{re.escape(keyword.lower())}\b"
            if re.search(pattern, note):
                return rule.get("points", DEFAULT_POINTS)

    return DEFAULT_POINTS
