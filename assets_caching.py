from pathlib import Path

from economy.gamba.utils import rounded_card_crop
from user_profile.utils import rounded_crop

ASSET_CACHE = {}
BADGE_CACHE = {}
FONTS = {}
ROCKS_CACHE = {}
RARITY_CACHE = {}

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = BASE_DIR / "assets/fonts"

CARD_CACHE = {}


NUM_MAP = {
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "10",
    11: "J",
    12: "Q",
    13: "K",
    14: "A",
}

SUIT_MAP = {
    1: "D",
    2: "H",
    3: "C",
    4: "S",
}

BADGE_TO_IMAGE = {
    "Beta Tester White": ASSETS_DIR / "beta_white.png",
    "Beta Tester Black": ASSETS_DIR / "beta_black.png",
    "Beta Tester Green": ASSETS_DIR / "beta_green.png",
    "Guild Founder": ASSETS_DIR / "oathfounder.png",
    "AQW Founder": ASSETS_DIR / "founderaqw.png",
    "Achievement Badges I": ASSETS_DIR / "aqwbadges1.png",
    "Achievement Badges II": ASSETS_DIR / "aqwbadges2.png",
    "Achievement Badges III": ASSETS_DIR / "aqwbadges3.png",
    "Achievement Badges IV": ASSETS_DIR / "aqwbadges4.png",
    "Epic Journey I": ASSETS_DIR / "epic1.png",
    "Epic Journey II": ASSETS_DIR / "epic2.png",
    "Epic Journey III": ASSETS_DIR / "epic3.png",
    "Epic Journey IV": ASSETS_DIR / "epic4.png",
    "Class Collector I": ASSETS_DIR / "class1.png",
    "Class Collector II": ASSETS_DIR / "class2.png",
    "Class Collector III": ASSETS_DIR / "class3.png",
    "Class Collector IV": ASSETS_DIR / "class4.png",
    "51% Weapons I": ASSETS_DIR / "weapon1.png",
    "51% Weapons II": ASSETS_DIR / "weapon2.png",
    "51% Weapons III": ASSETS_DIR / "weapon3.png",
    "51% Weapons IV": ASSETS_DIR / "weapon4.png",
    "Whale I": ASSETS_DIR / "whale1.webp",
    "Whale II": ASSETS_DIR / "whale2.webp",
    "Whale III": ASSETS_DIR / "whale3.webp",
    "Whale IV": ASSETS_DIR / "whale4.webp",
}


def initialize_assets():
    from PIL import Image, ImageFont

    def load(name, size=None):
        img = Image.open(ASSETS_DIR / name).convert("RGBA")
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)
        return img

    CARD_CACHE["blackjack"] = Image.open(ASSETS_DIR / "blackjack.png").convert("RGBA")

    CARD_CACHE["cardback"] = (
        Image.open(ASSETS_DIR / "cardback.png").convert("RGBA").resize((108, 171))
    )

    for suit in range(1, 5):
        for value in range(2, 15):
            path = ASSETS_DIR / f"{NUM_MAP[value]}{SUIT_MAP[suit]}.png"
            img = Image.open(path).convert("RGBA")
            img = rounded_card_crop(img, 104, 169, 22)
            CARD_CACHE[(suit, value)] = img

    # --- UI Assets ---
    ASSET_CACHE["coin"] = load("coin.png", (26, 27))
    ASSET_CACHE["trophy"] = load("trophy.png", (24, 24))
    ASSET_CACHE["podium"] = load("podium.png", (30, 30))
    ASSET_CACHE["gem"] = load("gem.png", (27, 27))
    ASSET_CACHE["medal"] = load("medal.png", (27, 27))
    ASSET_CACHE["dice"] = load("dice.png", (24, 24))
    ASSET_CACHE["messages"] = load("messages.png", (25, 25))
    ASSET_CACHE["aqwordle"] = load("aqwordle.webp", (26, 26))
    ASSET_CACHE["average"] = load("average.png", (27, 27))
    ASSET_CACHE["ticket"] = load("ticket.png", (25, 25))

    ASSET_CACHE["potw_border"] = load("potw_border.webp", (226, 241))
    ASSET_CACHE["potw_flare"] = load("potw_flare.webp", (42, 42))

    ASSET_CACHE["default_bg"] = load("default.png")

    # --- Badges ---
    for name, path in BADGE_TO_IMAGE.items():
        img = Image.open(path).convert("RGBA")
        img = img.resize((70, 70), Image.Resampling.LANCZOS)
        img = rounded_crop(img, 69, 14)
        BADGE_CACHE[name] = img

    # --- Fonts ---
    FONTS["big"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 54)
    FONTS["bold"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 66)
    FONTS["light"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 24)
    FONTS["small"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 30)
    FONTS["small_bold"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 27)
    FONTS["xsmall"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 24)
    FONTS["xsmall_bold"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 24)
    FONTS["xsmall_light"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 21)

    ROCK_SIZE = (150, 150)

    ROCKS_CACHE[1] = load("rock1.png", ROCK_SIZE)
    ROCKS_CACHE[2] = load("rock2.png", ROCK_SIZE)
    ROCKS_CACHE[3] = load("rock3.png", ROCK_SIZE)
    ROCKS_CACHE[4] = load("rock4.png", ROCK_SIZE)
    ROCKS_CACHE[5] = load("rock5.png", ROCK_SIZE)
    ROCKS_CACHE[6] = load("rock6.png", ROCK_SIZE)
    ROCKS_CACHE[7] = load("rock_gem1.png", ROCK_SIZE)
    ROCKS_CACHE[8] = load("rock_gem2.png", ROCK_SIZE)
    ROCKS_CACHE[9] = load("rock_gold.png", ROCK_SIZE)
    # ROCKS_CACHE[0] = load("dusty.png", ROCK_SIZE)
    ROCKS_CACHE[10] = load("broken_rock1.png", ROCK_SIZE)
    ROCKS_CACHE[11] = load("broken_rock2.png", ROCK_SIZE)
    ROCKS_CACHE[12] = load("broken_rock3.png", ROCK_SIZE)
    ROCKS_CACHE[13] = load("broken_rock4.png", ROCK_SIZE)
    ROCKS_CACHE[14] = load("broken_rock5.png", ROCK_SIZE)
    ROCKS_CACHE[15] = load("broken_rock6.png", ROCK_SIZE)
    ROCKS_CACHE[16] = load("broken_rock_gold.png", ROCK_SIZE)

    RARITY_CACHE["common"] = load("common.png", (26, 26))
    RARITY_CACHE["uncommon"] = load("uncommon.png", (26, 26))
    RARITY_CACHE["rare"] = load("rare.png", (26, 26))
    RARITY_CACHE["epic"] = load("epic.png", (26, 26))
    RARITY_CACHE["legendary"] = load("legendary.png", (26, 26))
