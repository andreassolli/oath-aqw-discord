import json
from pathlib import Path
import re
import requests
from datetime import date, datetime, timedelta
import requests

BASE_URL = "https://api.apps.web.id/someonlyclub/shop"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://api.apps.web.id/",
}

session = requests.Session()
session.headers.update(HEADERS)


def get_shop_ids():
    """Returns all unique shop IDs."""

    response = session.get(BASE_URL, timeout=10)
    response.raise_for_status()

    shops = response.json()

    # Remove duplicates while preserving order
    seen = set()
    ids = []

    for shop in shops:
        shop_id = int(shop["shop_id"])
        if shop_id not in seen:
            seen.add(shop_id)
            ids.append(shop_id)

    return ids


def get_shop_items(shop_id: int):
    response = session.get(f"{BASE_URL}/{shop_id}", timeout=10)
    response.raise_for_status()

    payload = response.json()

    if not payload:
        return []

    packet = json.loads(payload[0]["data"])
    shop = packet["b"]["o"]["shopinfo"]

    return [
        {
            "Name": item.get("sName"),
            "File": item.get("sFile"),
            "Link": item.get("sLink"),
            "Type": item.get("sType"),
        }
        for item in shop["items"]
    ]


def archive_all_items(output_file="items.json"):
    output = Path(output_file)

    if output.exists():
        items = json.loads(output.read_text(encoding="utf-8"))
    else:
        items = []

    # Prevent duplicates
    existing = {item["Link"] for item in items}

    for shop_id in get_shop_ids():
        try:
            shop_items = get_shop_items(shop_id)

            added = 0

            for item in shop_items:
                if item["Link"] not in existing:
                    existing.add(item["Link"])
                    items.append(item)
                    added += 1

            output.write_text(
                json.dumps(items, indent=4, ensure_ascii=False),
                encoding="utf-8",
            )

            print(f"✓ Shop {shop_id}: +{added} items")

        except Exception as e:
            print(f"✗ Shop {shop_id}: {e}")




if __name__ == "__main__":




    rotation = ["GOLD", "REP", "CLASS", "EXP"]

    anchor = date.fromisoformat("2025-08-04")

    specials = {
        "2025-08-01": "ALL",
        "2025-08-29": "ALL",
        "2025-10-03": "ALL",
        "2025-10-06": "ALL",
        "2025-10-17": "TRIPLE",
        "2025-10-31": "ALL",
        "2025-11-26": "ALL",
        "2025-11-27": "ALL",
        "2025-11-28": "ALL",
        "2025-11-29": "ALL",
        "2025-11-30": "ALL",
        "2025-12-24": "ALL",
        "2026-01-02": "ALL",
        "2026-01-30": "ALL",
        "2026-02-27": "ALL",
        "2026-03-27": "ALL",
        "2026-05-01": "ALL",
        "2026-05-29": "ALL",
        "2026-06-26": "ALL",
        "2026-07-31": "ALL",
        "2026-08-28": "ALL",
        "2026-09-25": "ALL",
        "2026-10-30": "ALL",
        "2026-11-25": "ALL",
        "2026-11-27": "ALL",
        "2026-12-25": "ALL",
        "2026-12-28": "ALL",
        "2026-12-30": "ALL",
        "2027-01-01": "ALL",
    }

    EMBED_COLORS = {
        "GOLD": 0xf1c40f,
        "REP": 0x3498db,
        "CLASS": 0x9b59b6,
        "EXP": 0x2ecc71,
        "ALL": 0xe74c3c,
        "TRIPLE": 0xff6600,
    }

    EMBED_ICONS = {
        "GEMS": "<:gems:1485660490376937502>",
        "COINS": "<:oathcoin:1462999179998531614>",
        "GOLD": "<:boostGold:1532786448141652069>",
        "REP": "<:boostRep:1532786499823734974>",
        "CLASS": "<:boostClass:1532786580215955636>",
        "EXP": "<:boostXP:1532786387625967857>",
        "ALL": "<:boostGold:1532786448141652069><:boostRep:1532786499823734974><:boostClass:1532786580215955636><:boostXP:1532786387625967857>",
        "TRIPLE": "<:boostGold:1532786448141652069><:boostRep:1532786499823734974><:boostClass:1532786580215955636><:boostXP:1532786387625967857>",
    }


    def boost_title(boost):
        return {
            "GOLD": "Double Gold Boost",
            "REP": "Double Reputation Boost",
            "CLASS": "Double Class Points Boost",
            "EXP": "Double Experience Boost",
            "ALL": "Double ALL Boost",
            "TRIPLE": "TRIPLE ALL Boost",
            "GEMS": "Double Gems Boost",
            "COINS": "Double Coins Boost",
        }.get(boost, boost)


    def get_boost_info(d: date):
        # Walk backwards until we reach the last reset day (Mon/Wed/Fri)
        boost_date = d
        while boost_date.weekday() not in (0, 2, 4):
            boost_date -= timedelta(days=1)

        key = boost_date.isoformat()

        weeks = (boost_date - anchor).days // 7

        offset = {
            0: 0,  # Monday
            2: 1,  # Wednesday
            4: 2,  # Friday
        }[boost_date.weekday()]

        slot = weeks * 3 + offset

        return {
            "boost": specials.get(key, rotation[slot % len(rotation)]),
            "alternateBoost": "GEMS" if slot % 2 == 0 else "COINS",
            "started": boost_date,
        }


    info = get_boost_info(date.today())
    started_ts = int(
        datetime.combine(info["started"], time.min).timestamp()
    )

    if info is None:
        raise SystemExit("No boost today.")

    payload = {
        "embeds": [
            {
                "title": f"{EMBED_ICONS[info['boost']]} {boost_title(info['boost'])} & {EMBED_ICONS[info['alternateBoost']]} {boost_title(info['alternateBoost'])} Active",
                "description": "A new server boost has just begun! Log in and make the most of it while it lasts.",
                "color": EMBED_COLORS[info["boost"]],
                "fields": [
                    {
                        "name": "Current AQW Boost",
                        "value": boost_title(info["boost"]),
                        "inline": True,
                    },
                    {
                        "name": "Current Oath Boost",
                        "value": boost_title(info["alternateBoost"]),
                        "inline": True,
                    },
                    {
                        "name": "Started",
                        "value": f"<t:{started_ts}:F>",
                        "inline": True,
                    },
                ],
                "footer": {
                    "text": "AQWorlds & Oath Boost Rotation",
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]
    }

    r = requests.post(WEBHOOK_URL, json=payload)

    print(r.status_code)
    print(r.text)
