import json
from pathlib import Path

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
    archive_all_items()
