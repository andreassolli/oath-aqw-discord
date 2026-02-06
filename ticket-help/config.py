import os

from dotenv import load_dotenv

load_dotenv()


def env_int(name: str) -> int:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing environment variable: {name}")
    return int(value)


TOKEN = os.getenv("DISCORD_TOKEN")
TICKET_COUNTER_FILE = "ticket_counter.txt"
HELPER_ROLE_ID = env_int("HELPER_ROLE_ID")
TICKET_LOG_CHANNEL_ID = env_int("TICKET_LOG_CHANNEL_ID")
TICKET_CATEGORY_ID = env_int("TICKET_CATEGORY_ID")
TICKET_CHANNEL_ID = env_int("TICKET_CHANNEL_ID")
ADMIN_ROLE_ID = env_int("ADMIN_ROLE_ID")
LEADERBOARD_CHANNEL_ID = env_int("LEADERBOARD_CHANNEL_ID")
WEEKLY_REQUESTER_CAP = env_int("WEEKLY_REQUESTER_CAP")
DISCORD_MANAGER_ROLE_ID = env_int("DISCORD_MANAGER_ROLE_ID")
OATHSWORN_ROLE_ID = env_int("OATHSWORN_ROLE_ID")
GUIDE_CHANNEL_ID = env_int("GUIDE_CHANNEL_ID")
