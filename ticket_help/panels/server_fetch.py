import aiohttp


async def fetch_servers():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://game.aq.com/game/api/data/servers") as response:
            data = await response.json()

    # filter only chat-enabled servers
    return [s for s in data if s.get("iChat") != 0 and s.get("bOnline") == 1]
