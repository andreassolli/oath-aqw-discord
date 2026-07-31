import json
from datetime import date, datetime
from zoneinfo import ZoneInfo

AQ_TZ = ZoneInfo("America/New_York")


class BoostSchedule:
    def __init__(self, path="boost_schedule.json"):
        with open(path) as f:
            data = json.load(f)

        self.rotation = data["rotation"]
        self.anchor = date.fromisoformat(data["anchor"]["date"])
        self.specials = data["specialBoosts"]

    def get_boost(self, d: date):
        key = d.isoformat()

        if key in self.specials:
            return self.specials[key]

        weekday = d.weekday()

        if weekday not in (0, 2, 4):
            return None

        weeks = (d - self.anchor).days // 7

        offset = {
            0: 0,
            2: 1,
            4: 2,
        }[weekday]

        slot = weeks * 3 + offset

        return self.rotation[slot % 4]

    def current_boost(self):
        return self.get_boost(datetime.now(AQ_TZ).date())

    def gold_active(self):
        return self.current_boost() == "GOLD"

    def rep_active(self):
        return self.current_boost() == "REP"

    def exp_active(self):
        return self.current_boost() == "CLASS"

    def class_active(self):
        return self.current_boost() == "EXP"



boost_schedule = BoostSchedule()
