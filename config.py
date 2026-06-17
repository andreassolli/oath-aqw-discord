import json
import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()


class RoleData(TypedDict):
    name: str
    id: int
    subtitle: str
    emoji: str
    emoji_id: int | None


def env_int(name: str) -> int:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing environment variable: {name}")
    return int(value)


VERY_TEMP_CHANNEL = 1505883810514862140
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
ASCENDED_ROLE_ID = env_int("ASCENDED_ROLE_ID")
TICKET_INSPECTORS_CHANNEL_ID = env_int("TICKET_INSPECTORS_CHANNEL_ID")
ROLES_CHANNEL_ID = env_int("ROLES_CHANNEL_ID")
COUNTING_CHANNEL_ID = env_int("COUNTING_CHANNEL_ID")
TICKET_INSPECTOR_ROLE_ID = env_int("TICKET_INSPECTOR_ROLE_ID")
TICKET_OFFICER_ROLE_ID = env_int("TICKET_OFFICER_ROLE_ID")
NEWS_WEBHOOK_URL = os.getenv("NEWS_WEBHOOK_URL")
DRAKATH_CERTIFICATE_ID = env_int("DRAKATH_CERTIFICATE_ID")
DAGE_CERTIFICATE_ID = env_int("DAGE_CERTIFICATE_ID")
DRAGO_CERTIFICATE_ID = env_int("DRAGO_CERTIFICATE_ID")
DARKON_CERTIFICATE_ID = env_int("DARKON_CERTIFICATE_ID")
SPEAKER_CERTIFICATE_ID = env_int("SPEAKER_CERTIFICATE_ID")
GRAMIEL_CERTIFICATE_ID = env_int("GRAMIEL_CERTIFICATE_ID")
NULGATH_CERTIFICATE_ID = env_int("NULGATH_CERTIFICATE_ID")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
OATH_USER_ID = env_int("OATH_USER_ID")
HELPER_CHANNEL_ID = env_int("HELPER_CHANNEL_ID")
GAMBA_UPDATES_CHANNEL_ID = env_int("GAMBA_UPDATES_CHANNEL_ID")
ASCENDED_ROLE_CHANNEL_ID = env_int("ASCENDED_ROLE_CHANNEL_ID")
TRANSCENDED_ROLE_ID = env_int("TRANSCENDED_ROLE_ID")
MIDNIGHT_MOSS = env_int("MIDNIGHT_MOSS")
ROYAL_VANGUARD = env_int("ROYAL_VANGUARD")
VERDANT_EMBER = env_int("VERDANT_EMBER")
VOX_ROLE = env_int("VOX_ROLE")
ANNOUNCEMENT_CHANNEL_ID = env_int("ANNOUNCEMENT_CHANNEL_ID")
RULES_CHANNEL_ID = env_int("RULES_CHANNEL_ID")
GUILD_LOG_CHANNEL_ID = env_int("GUILD_LOG_CHANNEL_ID")
GUILD_MEMBERS_COUNT = env_int("GUILD_MEMBERS_COUNT")
LFG_LOL_ID = env_int("LFG_LOL_ID")
TICKET_MESSAGES_CHANNEL_ID = env_int("TICKET_MESSAGES_CHANNEL_ID")
VERDANT_ROLE_ID = env_int("VERDANT_ROLE_ID")
CRIMSON_FLAME_ROLE_ID = env_int("CRIMSON_FLAME_ROLE_ID")
VOID_ROLE_ID = env_int("VOID_ROLE_ID")
CELESTIAL_ROLE_ID = env_int("CELESTIAL_ROLE_ID")

GOLF_GAMES_ROLE_ID = env_int("GOLF_GAMES_ROLE_ID")
MOVIES_ROLE_ID = env_int("MOVIES_ROLE_ID")
AQWORDLE_ROLE_ID = env_int("AQWORDLE_ROLE_ID")

ANNOUNCEMENTS_ROLE_ID = env_int("ANNOUNCEMENTS_ROLE_ID")
BADGES_ROLE_ID = env_int("BADGES_ROLE_ID")
EVENTS_ROLE_ID = env_int("EVENTS_ROLE_ID")
SCREENIES_ROLE_ID = env_int("SCREENIES_ROLE_ID")
BIRTHDAYS_ROLE_ID = env_int("BIRTHDAYS_ROLE_ID")


COLOR_ROLES = {
    VERDANT_EMBER,
    ROYAL_VANGUARD,
    MIDNIGHT_MOSS,
    VERDANT_ROLE_ID,
    CRIMSON_FLAME_ROLE_ID,
    VOID_ROLE_ID,
    CELESTIAL_ROLE_ID,
}
COLOR_ROLE_DATA: list[RoleData] = [
    {
        "name": "Verdant",
        "id": VERDANT_ROLE_ID,
        "emoji": "🌱",
        "emoji_id": None,
        "subtitle": "Embrace natures verdant color.",
    },
    {
        "name": "Crimson Flame",
        "id": CRIMSON_FLAME_ROLE_ID,
        "emoji": "🔥",
        "emoji_id": None,
        "subtitle": "Engulf yourself in crimson flames.",
    },
    {
        "name": "Void",
        "id": VOID_ROLE_ID,
        "emoji": "🔮",
        "emoji_id": None,
        "subtitle": "Slip into the void, slowly.",
    },
    {
        "name": "Celestial",
        "id": CELESTIAL_ROLE_ID,
        "emoji": "leftwing",
        "emoji_id": 1505157673249935402,
        "subtitle": "To the skies and beyond.",
    },
]

SOCIAL_ROLE_DATA: list[RoleData] = [
    {
        "name": "Golf Games",
        "id": GOLF_GAMES_ROLE_ID,
        "emoji": "⛳",
        "emoji_id": None,
        "subtitle": "Golf It, get it on Steam!",
    },
    {
        "name": "Movies",
        "id": MOVIES_ROLE_ID,
        "emoji": "🎬",
        "emoji_id": None,
        "subtitle": "Cozy up and watch movies",
    },
    {
        "name": "AQWordle",
        "id": AQWORDLE_ROLE_ID,
        "emoji": "🧩",
        "emoji_id": None,
        "subtitle": "Daily Wordle based on AQW",
    },
]

NOTIFICATION_ROLE_DATA: list[RoleData] = [
    {
        "name": "Announcements",
        "id": ANNOUNCEMENTS_ROLE_ID,
        "emoji": "📢",
        "emoji_id": None,
        "subtitle": "Larger server changes",
    },
    {
        "name": "Badges",
        "id": BADGES_ROLE_ID,
        "emoji": "aqwbadges4",
        "emoji_id": 1509937420106203368,
        "subtitle": "New AQW badge releases",
    },
    {
        "name": "Events",
        "id": EVENTS_ROLE_ID,
        "emoji": "🎉",
        "emoji_id": None,
        "subtitle": "Such as Outfit Contests",
    },
    {
        "name": "Screenies",
        "id": SCREENIES_ROLE_ID,
        "emoji": "📸",
        "emoji_id": None,
        "subtitle": "Guild Screenshots",
    },
    {
        "name": "Birthdays",
        "id": BIRTHDAYS_ROLE_ID,
        "emoji": "🎂",
        "emoji_id": None,
        "subtitle": "Congratulate others!",
    },
    {
        "name": "Helper",
        "id": HELPER_ROLE_ID,
        "emoji": "hands",
        "emoji_id": 1505158458494681138,
        "subtitle": "See tickets, and earn points!",
    },
]
ROLE_GROUPS: dict[str, list[RoleData]] = {
    "color": COLOR_ROLE_DATA,
    "social": SOCIAL_ROLE_DATA,
    "notification": NOTIFICATION_ROLE_DATA,
}
