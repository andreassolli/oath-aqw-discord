import json
from datetime import date, datetime, timedelta
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
        # Find the most recent reset day (Mon/Wed/Fri)
        boost_date = d
        while boost_date.weekday() not in (0, 2, 4):
            boost_date -= timedelta(days=1)

        weeks = (boost_date - self.anchor).days // 7

        offset = {
            0: 0,  # Monday
            2: 1,  # Wednesday
            4: 2,  # Friday
        }[boost_date.weekday()]

        slot = weeks * 3 + offset

        aqw_boost = self.specials.get(
            boost_date.isoformat(),
            self.rotation[slot % len(self.rotation)],
        )

        # Alternates every reset
        secondary_boost = "GEMS" if slot % 2 == 0 else "COINS"

        return aqw_boost, secondary_boost

    def current_boost(self):
        return self.get_boosts(datetime.now(AQ_TZ).date())[0]

    def current_secondary_boost(self):
        return self.get_boosts(datetime.now(AQ_TZ).date())[1]

    def coins_active(self):
        return self.current_secondary_boost() == "COINS"

    def gems_active(self):
        return self.current_secondary_boost() == "GEMS"

    def all_active(self):
        return self.current_boost() == "ALL"

    def triple_active(self):
        return self.current_boost() == "TRIPLE"


boost_schedule = BoostSchedule()
