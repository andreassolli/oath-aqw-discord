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

    def get_boosts(self, d: date):
        key = d.isoformat()

        weekday = d.weekday()

        if weekday not in (0, 2, 4):
            return None, None

        weeks = (d - self.anchor).days // 7

        offset = {
            0: 0,
            2: 1,
            4: 2,
        }[weekday]

        slot = weeks * 3 + offset

        aqw_boost = self.specials.get(key, self.rotation[slot % len(self.rotation)])

        # Alternates every reset
        secondary_boost = "COINS" if slot % 2 == 0 else "GEMS"

        return aqw_boost, secondary_boost

    def current_boost(self):
        return self.get_boosts(datetime.now(AQ_TZ).date())[0]

    def current_secondary_boost(self):
        return self.get_boosts(datetime.now(AQ_TZ).date())[1]

    def gold_active(self):
        return self.current_boost() == "GOLD"

    def rep_active(self):
        return self.current_boost() == "REP"

    def exp_active(self):
        return self.current_boost() == "CLASS"

    def class_active(self):
        return self.current_boost() == "EXP"

    def coins_active(self):
        return self.current_secondary_boost() == "COINS"

    def gems_active(self):
        return self.current_secondary_boost() == "GEMS"

    def triple_active(self):
        return self.current_boost() == "TRIPLE"




boost_schedule = BoostSchedule()
