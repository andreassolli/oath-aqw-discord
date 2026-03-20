import json
import os

from dotenv import load_dotenv

load_dotenv()


def env_int(name: str) -> int:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing environment variable: {name}")
    return int(value)


BOT_GUY_ROLE_ID = env_int("BOT_GUY_ROLE_ID")
EVENT_CHANNEL_ID = env_int("EVENT_CHANNEL_ID")
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
VERIFICATION_CHANNEL_ID = env_int("VERIFICATION_CHANNEL_ID")
MEE6_API = "https://mee6.xyz/api/plugins/levels/leaderboard/"
COUNTBOT_API = "https://count.bot/api/countbot/users/"
APPLICATION_ID = env_int("APPLICATION_ID")
AQW_INVENTORY = "https://account.aq.com/CharPage/inventory?ccid="
AQW_BADGES = "https://account.aq.com/CharPage/badges?ccid="
AQW_CHAR_PAGE = "https://account.aq.com/CharPage?id="
CCID_PAGE = "https://game.aq.com/game/api/charpage/fvars?id="
TEAM_CATEGORY_ID = env_int("TEAM_CATEGORY_ID")
OFFICER_ROLE_ID = env_int("OFFICER_ROLE_ID")
spam_points = [15, 30, 50, 75, 105, 145, 190, 240, 295, 300]
percentage_points = {1: 4, 2: 3, 5: 2, 0.1: 10}
BADGE_CHANNEL_ID = env_int("BADGE_CHANNEL_ID")
UNSWORN_ROLE_ID = env_int("UNSWORN_ROLE_ID")
INITIATE_ROLE_ID = env_int("INITIATE_ROLE_ID")
STRANGER_ROLE_ID = env_int("STRANGER_ROLE_ID")
POTW_ROLE_ID = env_int("POTW_ROLE_ID")
OFFICER_CHANNEL_ID = env_int("OFFICER_CHANNEL_ID")
LORE_CHANNEL_ID = env_int("LORE_CHANNEL_ID")
POTW_THREAD_ID = env_int("POTW_THREAD_ID")
# BADGES
FORGE_BADGE = env_int("FORGE_BADGE")
WHALE_BADGE = env_int("WHALE_BADGE")
WEAPON_BADGE = env_int("WEAPON_BADGE")
FOUNDER_BADGE = env_int("FOUNDER_BADGE")
EPIC_BADGE = env_int("EPIC_BADGE")
COLLECTION_BADGE = env_int("COLLECTION_BADGE")

COLLECTION_CHEST_URL = "http://aqwwiki.wikidot.com/list-of-all-collection-chests"
WEAPON_SHEET = os.getenv("WEAPON_SHEET")
CLASSES_SHEET = os.getenv("CLASSES_SHEET")

BADGES = [
    # "Forge",
    # "Forge+",
    # "Whale",
    "51% Weapons",
    "Class Collector",
    "Achievement Badges",
    "Epic Journey",
    "Whale",
    "AQW Founder",
]

SPAM_CMD_CHANNEL_ID = env_int("SPAM_CMD_CHANNEL_ID")
SPAM_BOTS_CHANNEL_ID = env_int("SPAM_BOTS_CHANNEL_ID")
TESTING_CHANNEL_ID = env_int("TESTING_CHANNEL_ID")
LOBBY_CHANNEL_ID = env_int("LOBBY_CHANNEL_ID")

GUILD_ID = env_int("GUILD_ID")
BOSS_TO_SHEET = json.loads(os.getenv("BOSS_TO_SHEET", "{}"))

BOSS_TYPES: dict[str, str] = {
    "standard": "Standard",
    "darkon": "Ultra Darkon",
    "gramiel": "Ultra Gramiel",
    "drakath": "Champion Drakath",
    "dage": "Ultra Dage",
    "nulgath": "Ultra Nulgath",
    "drago": "Ultra Drago",
    "speaker": "Ultra Speaker",
}

CLASS_IMAGES_SHEET: str = os.getenv("CLASS_IMAGES_SHEET") or ""
BANNED_LIST_CHANNEL_ID = env_int("BANNED_LIST_CHANNEL_ID")
LEADERBOARD_HISTORY_CHANNEL_ID = env_int("LEADERBOARD_HISTORY_CHANNEL_ID")
OATH_EVENT_CHANNEL_ID = env_int("OATH_EVENT_CHANNEL_ID")
NEW_TICKET_CATEGORY_ID = env_int("NEW_TICKET_CATEGORY_ID")
PROXY_SERVICE = os.getenv("PROXY_SERVICE")
BETA_TESTING_CHANNEL_ID = env_int("BETA_TESTING_CHANNEL_ID")
BETA_TESTER_ROLE_ID = env_int("BETA_TESTER_ROLE_ID")
MODERATOR_ROLE_ID = env_int("MODERATOR_ROLE_ID")
COMMUNITY_FEEDBACK_CHANNEL_ID = env_int("COMMUNITY_FEEDBACK_CHANNEL_ID")
ALLOWED_COMMANDS_CHANNELS = {
    SPAM_CMD_CHANNEL_ID,
    SPAM_BOTS_CHANNEL_ID,
    TESTING_CHANNEL_ID,
    BETA_TESTING_CHANNEL_ID,
}
UNSOLVED_TAG_ID = env_int("UNSOLVED_TAG_ID")
REPORT_TAG_ID = env_int("REPORT_TAG_ID")
SOLVED_TAG_ID = env_int("SOLVED_TAG_ID")
MAPRIL_ROLE_ID = env_int("MAPRIL_ROLE_ID")
OG_SAN_ID = env_int("OG_SAN_ID")
EXPERIENCED_HELPER_ROLE_ID = env_int("EXPERIENCED_HELPER_ROLE_ID")
