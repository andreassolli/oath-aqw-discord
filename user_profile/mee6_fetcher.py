import aiohttp

from config import MEE6_API


async def fetch_mee6_stats(user_id: int, server_id: int):
    async with aiohttp.ClientSession() as session:
        page = 0

        while True:
            url = f"{MEE6_API}{server_id}?page={page}"

            async with session.get(url) as resp:
                if resp.status != 200:
                    break

                data = await resp.json()
                players = data.get("players", [])

                # no more users → stop
                if not players:
                    break

                for player in players:
                    if int(player["id"]) == user_id:
                        return {
                            "level": player["level"],
                            "current_xp": player["detailed_xp"][0],
                            "xp_to_level": player["detailed_xp"][1],
                            "messages": player["message_count"],
                        }

                page += 1  # go next page

    # fallback if not found
    return {
        "level": 0,
        "current_xp": 0,
        "xp_to_level": 100,
        "messages": 0,
    }
