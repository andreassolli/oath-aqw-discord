from mee6_fetcher import fetch_mee6_stats
from PIL import Image, ImageDraw, ImageFont
from utils import circle_crop, fetch_avatar

AVATAR_PATH = "assets/default-avatar.jpg"
BACKGROUND_PATH = "assets/card.png"


async def generate_profile_card(interaction):
    user_id = interaction.user.id
    server_id = interaction.guild.id
    mee6 = await fetch_mee6_stats(user_id, server_id)
    bg = Image.open(BACKGROUND_PATH).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    avatar = await fetch_avatar(interaction.user.display_avatar.url)
    avatar = circle_crop(avatar, 154)

    # Paste position (x, y)
    bg.paste(avatar, (29, 21), avatar)

    font_big = ImageFont.truetype("Urbanist-Regular.ttf", 36)
    font_bold = ImageFont.truetype("Urbanist-Bold.ttf", 44)
    font_light = ImageFont.truetype("Urbanist-Light.ttf", 16)
    font_small = ImageFont.truetype("Urbanist-Regular.ttf", 20)
    font_xsmall = ImageFont.truetype("Urbanist-Regular.ttf", 14)

    draw.text((227, 21), "Proxy", font=font_big, fill="#FFFFFF")

    draw.text((227, 61), "Oath", font=font_small, fill="#A0A0AA")

    draw.text((227, 96), "Joined 2. feb 2026", font=font_light, fill="#A0A0AA")

    draw.text((29, 190), "Badges", font=font_small, fill="#FFFFFF")

    draw.text((237, 131), "Stats", font=font_small, fill="#FFFFFF")

    draw.text((252, 154), str(mee6["level"]), font=font_bold, fill="#FFFFFF")

    draw.text((240, 182), "lvl", font=font_xsmall, fill="#FFFFFF")

    draw.text(
        (240, 200),
        f"{mee6['current_xp']} / {mee6['xp_to_level']} xp",
        font=font_xsmall,
        fill="#A0A0AA",
    )

    draw.text((375, 168), f"{mee6['messages']} sent", font=font_xsmall, fill="#FFFFFF")

    draw.text((375, 198), "142 counts", font=font_xsmall, fill="#FFFFFF")

    draw.text((237, 247), "Tickets", font=font_small, fill="#FFFFFF")

    draw.text((267, 282), "215 helped", font=font_xsmall, fill="#FFFFFF")

    draw.text((267, 313), "215 points", font=font_xsmall, fill="#FFFFFF")

    draw.text((375, 282), "Won 2 times", font=font_xsmall, fill="#FFFFFF")

    draw.text((375, 313), "34th place", font=font_xsmall, fill="#FFFFFF")

    trophy = Image.open("trophy.png").convert("RGBA")
    trophy = trophy.resize((18, 18), Image.Resampling.LANCZOS)
    calendar = Image.open("calendar.png").convert("RGBA")
    calendar = calendar.resize((18, 18), Image.Resampling.LANCZOS)
    ticket = Image.open("ticket.png").convert("RGBA")
    ticket = ticket.resize((18, 18), Image.Resampling.LANCZOS)
    medal = Image.open("medal.png").convert("RGBA")
    medal = medal.resize((18, 18), Image.Resampling.LANCZOS)
    robot = Image.open("robot.png").convert("RGBA")
    robot = robot.resize((18, 18), Image.Resampling.LANCZOS)
    messages = Image.open("messages.png").convert("RGBA")
    messages = messages.resize((18, 18), Image.Resampling.LANCZOS)
    forge = Image.open("forge.png").convert("RGBA")
    forge = forge.resize((34, 34), Image.Resampling.LANCZOS)
    sword = Image.open("sword.png").convert("RGBA")
    sword = sword.resize((34, 34), Image.Resampling.LANCZOS)

    bg.paste(forge, (29, 224), forge)
    bg.paste(sword, (73, 224), sword)

    bg.paste(trophy, (350, 282), trophy)
    bg.paste(calendar, (350, 312), calendar)
    bg.paste(ticket, (242, 282), ticket)
    bg.paste(medal, (242, 313), medal)
    bg.paste(messages, (350, 168), messages)
    bg.paste(robot, (350, 198), robot)

    bg.save("final_profile_card.png")
