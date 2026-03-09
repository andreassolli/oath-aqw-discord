import asyncio
import json
import re

from curl_cffi.requests import AsyncSession

URL = "https://www.kickstarter.com/projects/artix/adventurequest-worlds-infinity"


async def update_kickstarter():
    async with AsyncSession(impersonate="chrome") as session:
        r = await session.get(URL)

        html = r.text

        # extract embedded JSON
        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
        )

        if not match:
            print("NEXT_DATA not found")
            print(html[:500])
            return

        data = json.loads(match.group(1))

        # navigate to rewards
        project = data["props"]["pageProps"]["project"]

        rewards = project["rewards"]

        for reward in rewards:
            print(
                reward["title"],
                reward["minimum"],
                reward["backersCount"],
                reward.get("remainingQuantity"),
            )


asyncio.run(update_kickstarter())
