import aiohttp
from config import MEE6_API


async def fetch_mee6_stats(user_id: int, server_id: int):
    url = f"{MEE6_API}{server_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    for player in data["players"]:
        if int(player["id"]) == user_id:
            return {
                "level": player["level"],
                "current_xp": player["detailed_xp"][0],
                "xp_to_level": player["detailed_xp"][1],
                "messages": player["message_count"],
            }

    return {"level": 0, "current_xp": 0, "xp_to_level": 100, "messages": 0}
