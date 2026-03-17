from urllib.parse import parse_qs

from config import PROXY_SERVICE
from http_client import get_session

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://account.aq.com/CharPage",
}


async def fetch_servers():
    url = "https://game.aq.com/game/api/data/servers"
    session = await get_session()

    async with session.get(url, headers=HEADERS, proxy=PROXY_SERVICE) as resp:
        data = await resp.json()

    # filter only chat-enabled + non-mem + online servers
    return [
        s
        for s in data
        if s.get("iChat") != 0 and s.get("bOnline") == 1 and s.get("bUpg") != 1
    ]
