import discord


def build_class_embed(
    *,
    class_name: str,
    general_loadout: dict[str, str],
    consumables: dict[str, str],
    image_url: str | None,
) -> discord.Embed:

    embed = discord.Embed(
        title=class_name,
        description="**Class Enhancement Setups**",
        color=discord.Color.blurple(),
    )

    # -------- General Section --------
    general_text = (
        "<:forge:1456909374562898093> **Enhancements**\n"
        f"<:swordaqw:1457810578994233434> - {general_loadout.get('sword', '—')}\n"
        f"<:classaqw:1457810673395433641> - {general_loadout.get('class', '—')}\n"
        f"<:helmaqw:1457810605443383307> - {general_loadout.get('helm', '—')}\n"
        f"<:cloakaqw:1457810628168253522> - {general_loadout.get('cloak', '—')}\n"
    )

    # -------- Consumables --------
    consumables_text = (
        "\n🧪 **Consumables**\n"
        f"<:elixir:1457810755050143754> - {consumables.get('elixir', '—')}\n"
        f"<:Tonic:1457810787702935635> - {consumables.get('tonic', '—')}\n"
        f"<:potion:1457810711706341544> - {consumables.get('consumable', '—')}"
    )

    embed.add_field(
        name="",
        value=general_text + consumables_text,
        inline=False,
    )

    embed.add_field(
        name="🎯 Need this class for a specific boss?",
        value="Click one of the buttons below for boss-specific setups!",
        inline=False,
    )

    if image_url:
        embed.set_image(url=image_url)

    return embed
