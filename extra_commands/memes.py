import discord

from class_setups.embed_class import build_class_embed


async def m_rcs(interaction: discord.Interaction):
    embed = discord.Embed(
        title="There's this new anime I'm watching...",
        color=discord.Color.purple(),
    )
    file = discord.File("assets/scar_anime.png", filename="scar_anime.png")
    embed.set_image(url="attachment://scar_anime.png")
    await interaction.response.send_message(embed=embed, file=file)


async def m_dryage(interaction: discord.Interaction):
    embed = discord.Embed(title="Like fine wine", color=discord.Color.purple())
    file = discord.File("assets/dryage.png", filename="dryage.png")
    embed.set_image(url="attachment://dryage.png")
    await interaction.response.send_message(embed=embed, file=file)


async def m_gld(interaction: discord.Interaction):
    embed = discord.Embed(
        description="Im gonna have to force some changes",
        color=discord.Color.purple(),
    )
    embed.set_footer(text="GL*D on Bottom")
    file = discord.File("assets/gld.png", filename="gld.png")
    embed.set_image(url="attachment://gld.png")
    await interaction.response.send_message(embed=embed, file=file)


async def m_mapril(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Duffer: official Duffer of Dufferville in st Duffersburg, population Duffer Mapril",
        color=discord.Color.purple(),
    )
    file = discord.File("assets/duffer_mapril.png", filename="duffer_mapril.png")
    embed.set_image(url="attachment://duffer_mapril.png")
    await interaction.response.send_message(embed=embed, file=file)


async def m_sker(interaction: discord.Interaction):
    embed = discord.Embed(title="I'M READY", color=discord.Color.purple())
    file = discord.File("assets/scr_weird.png", filename="scr_weird.png")
    embed.set_image(url="attachment://scr_weird.png")
    await interaction.response.send_message(embed=embed, file=file)


async def m_oath(interaction: discord.Interaction):
    embed = discord.Embed(title="To the Oath we Swear", color=discord.Color.purple())

    file = discord.File("assets/takeoath.gif", filename="takeoath.gif")
    embed.set_image(url="attachment://takeoath.gif")
    embed.add_field(
        name="",
        value=("I take no Throne, for there is no honor in tyranny!"),
        inline=True,
    )
    await interaction.response.send_message(embed=embed, file=file)


async def m_bigrig(interaction: discord.Interaction):
    embed = discord.Embed(
        description="Two take it or leave it!", color=discord.Color.purple()
    )
    file = discord.File("assets/bionicle.jpg", filename="bionicle.jpg")
    embed.set_image(url="attachment://bionicle.jpg")
    embed.set_footer(text="Hey its cold out...")
    await interaction.response.send_message(embed=embed, file=file)


async def m_juns(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Guys look at this crazy Alpha Omega class!",
        description="I do INSANE damage, INSANE healing! \nJust look at my Battle Analyzer, it's INSANE!",
        color=discord.Color.purple(),
    )
    file = discord.File("assets/juns.webp", filename="juns.webp")
    embed.set_image(url="attachment://juns.webp")
    await interaction.response.send_message(embed=embed, file=file)


async def m_og_san(interaction: discord.Interaction):
    file = discord.File("assets/ogsan.webp", filename="ogsan.webp")
    embed = build_class_embed(
        class_name="OG San",
        description="0 sleep, 0 points, we good to go! ",
        image_url="attachment://ogsan.webp",
        general_loadout={
            "sword": "Walking Cane",
            "class": "Blue Furry Suit",
            "cloak": "Sleep Paralysis Demons",
            "helm": "Gray Beard",
        },
        consumables={
            "elixir": "Unknown (Not Youth Elixir at least)",
            "tonic": "Placebo Speed",
            "consumable": "Copium",
        },
        is_class=False,
    )
    await interaction.response.send_message(embed=embed, file=file)


async def m_goon_greed(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Mr. Greed <:Huh:1457144254576197742>",
        description="",
        color=discord.Color.purple(),
    )
    file = discord.File("assets/goon_greed.png", filename="goon_greed.png")
    embed.set_image(url="attachment://goon_greed.png")
    await interaction.response.send_message(embed=embed, file=file)


async def m_og_pro(interaction: discord.Interaction):
    embed = discord.Embed(
        title="This guy <:lucyMad:1475264263252742184>",
        description="",
        color=discord.Color.blue(),
    )
    file = discord.File("assets/og-pro.webp", filename="og-pro.webp")
    embed.set_image(url="attachment://og-pro.webp")
    await interaction.response.send_message(embed=embed, file=file)


async def m_yokai(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Time to go",
        description="",
        color=discord.Color.blue(),
    )
    file = discord.File("assets/yokai.png", filename="yokai.png")
    embed.set_image(url="attachment://yokai.png")
    await interaction.response.send_message(embed=embed, file=file)
