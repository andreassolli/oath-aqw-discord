import json
import logging

import aiohttp

from config import COUNTBOT_API

log = logging.getLogger(__name__)


async def fetch_countbot_stats(user_id: int) -> int:
    url = f"{COUNTBOT_API}{user_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()

            if resp.status != 200:
                log.warning(
                    "CountBot API %s for user %s: %s",
                    resp.status,
                    user_id,
                    text.strip(),
                )
                return 0  # SAFE fallback

            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                log.error(
                    "CountBot returned non-JSON for user %s: %r",
                    user_id,
                    text[:200],
                )
                return 0

            return int(data.get("numbersCounted", 0))
