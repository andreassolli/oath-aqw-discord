from pathlib import Path

ASSET_CACHE = {}
BADGE_CACHE = {}
FONTS = {}


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = BASE_DIR / "assets/fonts"


BADGE_TO_IMAGE = {
    "Beta Tester1": ASSETS_DIR / "beta_tester1.png",
    "Beta Tester2": ASSETS_DIR / "beta_tester2.png",
    "Beta Tester3": ASSETS_DIR / "beta_tester3.png",
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

    # --- UI Assets ---
    ASSET_CACHE["trophy"] = load("coin.png", (27, 27))
    ASSET_CACHE["calendar"] = load("calendar.png", (27, 27))
    ASSET_CACHE["gem"] = load("gem.png", (27, 27))
    ASSET_CACHE["medal"] = load("medal.png", (27, 27))
    ASSET_CACHE["dice"] = load("dice.png", (27, 27))
    ASSET_CACHE["messages"] = load("messages.png", (27, 27))

    ASSET_CACHE["potw_border"] = load("potw_border.webp", (158, 168))
    ASSET_CACHE["potw_flare"] = load("potw_flare.webp", (42, 42))

    ASSET_CACHE["default_bg"] = load("card.png")

    # --- Badges ---
    for name, path in BADGE_TO_IMAGE.items():
        img = Image.open(path).convert("RGBA")
        img = img.resize((51, 51), Image.Resampling.LANCZOS)
        BADGE_CACHE[name] = img

    # --- Fonts ---
    FONTS["big"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 54)
    FONTS["bold"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 66)
    FONTS["light"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 24)
    FONTS["small"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 30)
    FONTS["xsmall"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 24)
    FONTS["xsmall_light"] = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 21)
