from textwrap import dedent

import discord
from discord import app_commands
from discord.ext import commands


class Forge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    forge = app_commands.Group(name="forge", description="Look up a Forge Enhancement")

    @forge.command(name="helm", description="Look up Base Forge Enhancement for Helm")
    async def helm(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent(
                """\
            <:helmaqw:1487000474014974054> **Forge Helmet Enhancement**
    <:aqwcheck:1532278320870326382> Must be Level 30.
    <:aqwcheck:1532278320870326382> Must have Rank 4 Blacksmithing.

    * <:spearaqw:1487000575290642553> 1st Lord of Chaos Staff  (🧟‍♂️Staff of Inversion, 📍 `/join escherion`)
    * <:axeaqw:1487000523268947988> Chaos Dragonlord Axe (🧟‍♂️Vath,📍 `/join stalagbite`)
    * <:swordaqw:1487004634307629056> Hanzamune Dragon Koi Blade (🧟‍♂️Kitsune,📍 `/join kitsune`)
    * <:axeaqw:1487000523268947988> Wrath of the Werepyre (🧟‍♂️Wolfwing,📍 `/join wolfwing`)
    """
            )
        )

    @forge.command(name="vim", description="Look up Vim Forge Enhancement for Helm")
    async def vim(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent(
                """\
            <:helmaqw:1487000474014974054> **Vim,Ether**
            > Special passive trait: -33% Mana Consumption
            <:aqwcheck:1532278320870326382> Must have completed the previous quest.
            <:aqwcheck:1532278320870326382> Must be Level 70.
            <:aqwcheck:1532278320870326382> Must have Rank 7 Blacksmithing.
            <:aqwcheck:1532278320870326382> Must have Rogue Rank 10 in your inventory. (💰 Metrea Shop, 📍`/join trainers`)
            * <:misc:1532256591141929031> Ethereal Essence `x250` (🧟‍♂️Various monsters,📍`/join towerofdoom` **❗️Room 6+ & larger number = larger drop rate**)
            """
            )
        )

    @forge.command(
        name="examen", description="Look up Examen Forge Enhancement for Helm"
    )
    async def examen(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent(
                """\
            <:helmaqw:1487000474014974054> **Examen, Ether**
            > Special passive trait: -33% Mana Consumption
            <:aqwcheck:1532278320870326382> Must have completed the previous quest.
            <:aqwcheck:1532278320870326382> Must be Level 70.
            <:aqwcheck:1532278320870326382> Must have Rank 7 Blacksmithing.
            <:aqwcheck:1532278320870326382> Must have Healer Rank 10 in your inventory. (💰 Juvania Shop, 📍`/join trainers`)
            * <:misc:1532256591141929031> Ethereal Essence `x250` (🧟‍♂️Various monsters,📍`/join towerofdoom` **❗️Room 6+ & larger number = larger drop rate**)"""
            )
        )

    @forge.command(name="anima", description="Look up Anima Forge Enhancement for Helm")
    async def anima(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent(
                """\
            <:helmaqw:1487000474014974054> **Anima, Clairvoyance**
            > Special passive trait: +10% Hit Chance
            <:aqwcheck:1532278320870326382> Must have completed the previous quest.
            <:aqwcheck:1532278320870326382> Must be Level 70.
            <:aqwcheck:1532278320870326382> Must have Rank 7 Blacksmithing.
            <:aqwcheck:1532278320870326382> Must have Warrior Rank 10 in your inventory. (💰 Thok Shop, 📍`/join trainers`)
            * <:misc:1532256591141929031> Ethereal Essence `x650` (🧟‍♂️Various monsters,📍`/join towerofdoom` **❗️Room 6+ & larger number = larger drop rate**)"""
            )
        )

    @forge.command(
        name="pneuma", description="Look up Pneuma Forge Enhancement for Helm"
    )
    async def pneuma(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent(
                """\
            <:helmaqw:1487000474014974054> **Penuma, Clairvoyance**
            > Special passive trait: +10% Hit Chance
            <:aqwcheck:1532278320870326382> Must have completed the previous quest.
            <:aqwcheck:1532278320870326382> Must be Level 70.
            <:aqwcheck:1532278320870326382> Must have Rank 7 Blacksmithing.
            <:aqwcheck:1532278320870326382> Must have Mage Rank 10 in your inventory. (💰 Arcana Shop, 📍`/join trainers`)
            * <:misc:1532256591141929031> Ethereal Essence `x650` (🧟‍♂️Various monsters,📍`/join towerofdoom` **❗️Room 6+ & larger number = larger drop rate**)"""
            )
        )

    @forge.command(name="cape", description="Look up Base Forge Enhancement for Cape")
    async def cape(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent(
                """\
            <:aqwCape:1501670762174746644> **Forge**
            - <:aqwcheck:1532278320870326382> Must have completed the 'Defeat Kitsune', part of 13th Lord of Chaos.
            - <:aqwcheck:1532278320870326382> Must be Level 30.
            - <:aqwcheck:1532278320870326382> Must have Rank 4 Blacksmithing.
            * <:aqwCape:1501670762174746644> Prismatic Celestial Wings  (🧟‍♂️ Diabolical Warlord, 📍  `/join lostruinswar`)
            * <:aqwCape:1501670762174746644> Broken Wings  (🧟‍♂️Infernal Warlord, 📍 `/join lostruins`)
            * <:aqwCape:1501670762174746644> Shadow's Wings  (🧟‍♂️Azkorath, 📍 `/join infernalspire`)
            * <:aqwCape:1501670762174746644> Wings Of Destruction  (🧟‍♂️Malxas, 📍 `/join infernalspire`)"""
            )
        )

    @forge.command(
        name="absolution", description="Look up Absolution Forge Enhancement for Cape"
    )
    async def absolution(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent(
                """\
            <:aqwCape:1501670762174746644> **Absolution**
            > +50% Healing Boost
            > -20% Physical Boost
            - <:aqwcheck:1532278320870326382> Must be Level 90.
            - <:aqwcheck:1532278320870326382> Must have Blacksmithing Rep rank 9, and Good Rep rank 10.
            * <:armoraqw:1487000736087670936> Ascended Paladin (💰 Slimed Sigil `x100` + 100 000 Gold, 📍`/join therift`)
            * <:swordaqw:1487004634307629056> Ascended Paladin Sword (💰 Slimed Sigil `x50` + 25 000 Gold, 📍`/join therift`)"""
            )
        )

    @forge.command(
        name="vainglory", description="Look up Vainglory Forge Enhancement for Cape"
    )
    async def vainglory(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
                <:aqwCape:1501670762174746644> **Vainglory**
        > +15% Damage Boost
        > -50% Healing Intake
        - <:aqwcheck:1532278320870326382> Must have completed the previous quest.
        - <:aqwcheck:1532278320870326382> Must be Level 90.
        - <:aqwcheck:1532278320870326382> Must have Rank 9 Blacksmithing.
        * <:misc:1532256591141929031>  Pauldron Relic `x1` ( 💰 Pauldron Fragment `x15`, 📍`/join museum`)
          - For Pauldron Fragment `x1`: Pauldron Shard `x15` (🧟‍♂️Ultra Akriloth,📍 `/join gravestrike`)
        * <:misc:1532256591141929031> Breastplate Relic `x1` ( 💰 Breastplate Fragment `x10` , 📍`/join museum`)
          - For Breastplate Fragment `x1`: Breastplate Shard`x10` (🧟‍♂️Carnax,📍 `/join aqlesson`)
        * <:misc:1532256591141929031> Vambrace Relic `x1`   (💰 Vambrace Fragment `x15`, `/join museum`)
          - For Vambrace Fragment `x1`:  Vambrace Shard `x15`(🧟‍♂️Ultra Blood Titan,📍 `/join bloodtitan`)
        * <:misc:1532256591141929031> Gauntlet Relic `x1` ( 💰 Gauntlet Fragment `x25` , 📍`/join museum`)
          - For Gauntlet Fragment `1`: Gauntlet Shard `x5`(🧟‍♂️Ultra Alteon,📍 `/join ultraalteon`)
        * <:misc:1532256591141929031> Greaves Relic `x1` ( 💰Greaves Fragment `x10`, 📍`/join museum`)
          - For Greaves Fragment `x1`: Greaves Shard `x15`(🧟‍♂️Mutated Void Dragon,📍 `/join bosschallenge`)""")
        )

    @forge.command(
        name="avarice", description="Look up Avarice Forge Enhancement for Cape"
    )
    async def avarice(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:aqwCape:1501670762174746644> **Avarice**
        > +10% Haste
        > -35% Damage Resistance
        - <:aqwcheck:1532278320870326382> Must have completed the previous quest.
        - <:aqwcheck:1532278320870326382> Must be Level 90.
        - <:aqwcheck:1532278320870326382> Must have Rank 9 Blacksmithing.
        - <:misc:1532256591141929031> Indulgence `x50` (<:queststart:1491012167170920560> 'Circles of Fate' , 📍`/join sevencircles`)
          - Essence of Luxuria `x1` (🧟‍♂️Luxuria /🧟‍♂️Luxuria Guard)
          - Essence of Gluttony `x1` (🧟‍♂️Gluttony /🧟‍♂️Gluttony Guard)
          - Essence of Avarice `x1`(🧟‍♂️Avarice /🧟‍♂️Avarice Guard)
          - Souls of Limbo `x25` (🧟‍♂️Limbo Guard)
        - <:misc:1532256591141929031> Penance `x50` (💰  Merge the stuff below 📍`/join sevencircleswar`)
          -  Essence of Wrath `x1`
          - Essence of Violence `x1`
          - Essence of Treachery `x1`
          - Souls of Heresy `x15`""")
        )

    @forge.command(
        name="penitence", description="Look up Penitence Forge Enhancement for Cape"
    )
    async def penitence(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:aqwCape:1501670762174746644> **Penitence**
        > +25% Damage Resistance
        > -25% DoT Boost
        <:aqwcheck:1532278320870326382> Must have completed the previous quest.
        <:aqwcheck:1532278320870326382> Must be Level 90.
        <:aqwcheck:1532278320870326382> Must have Rank 9 Blacksmithing.
        * <:spearaqw:1487000575290642553> Night Mare Scythe (<:queststart:1491012167170920560> 'Yulgar's Worst Nightmare', 📍`/join yulgar`)
          * (🧟‍♂️ Binky, 📍  `/join doomvault`)
        * <:misc:1532256591141929031> Sapphire Orb  `x100` (🧟‍♂️Legion Lich Lord, 📍 `/join frozenlair`)
        * <:spearaqw:1487000575290642553> Boreal Cavalier Bardiche (🧟‍♂️Warlord Icewing, 📍 `/join icewing`)
        * <:misc:1532256591141929031> Void Scale  `x13` (🧟‍♂️ArchFiend DragonLord, 📍 `/join underlair`)

        **Ultra Bosses**: Use if you have low health, and/or boss does a lot of damage which isn't True Damage. """)
        )

    @forge.command(
        name="lament", description="Look up Lament Forge Enhancement for Cape"
    )
    async def lament(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:aqwCape:1501670762174746644>**Lament**
        > +20% Critical Chance
        > -5% Haste
        <:aqwcheck:1532278320870326382> Must have completed the previous quest.
        <:aqwcheck:1532278320870326382> Must be Level 90.
        <:aqwcheck:1532278320870326382> Must have Rank 9 Blacksmithing.
        * <:misc:1532256591141929031> Doom Heart  (🧟‍♂️Ultra Sepulchure , 📍`/join sepulchurebattle`)
        * <:misc:1532256591141929031> Heart of the Sun  (<:queststart:1491012167170920560> Warlic's 'Mother Knows The Sun', 📍`/join thirdspell`)
        * <:misc:1532256591141929031> Flame Heart  `x10`  (🧟‍♂️Smoldur, 📍`/join ashfallcamp`)
        * <:misc:1532256591141929031> Bloodless Heart  `x3`  (🧟‍♂️Cured Phlegnn *or* Mutated Plague, 📍`/join sloth`)""")
        )

    @forge.command(
        name="weapon", description="Look up Base Forge Enhancement for Weapon"
    )
    async def sword(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:swordaqw:1487004634307629056>**Forge**
        - <:aqwcheck:1532278320870326382> Finished Mobius part of 13th Lord of Chaos
        - <:aqwcheck:1532278320870326382> Blacksmith Rep rank 4
        - <:aqwcheck:1532278320870326382> Level 30
        - <:helmaqw:1487000474014974054> 1st Lord Of Chaos Helm (🧟‍♂️Escherion, 📍`/join escherion`)
        - <:helmaqw:1487000474014974054> Chaos Dragonlord Helm (🧟‍♂️Vath, 📍`/join stalagbite`)
        - <:helmaqw:1487000474014974054> Chaos Shogun Helmet (🧟‍♂️Kitsune, 📍`/join kitsune`)
        - <:helmaqw:1487000474014974054> Wolfwing Mask (🧟‍♂️Vath, 📍`/join wolfwing`)""")
        )

    @forge.command(
        name="lacerate", description="Look up Lacerate Forge Enhancement for Weapon"
    )
    async def lacerate(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:swordaqw:1487004634307629056>**Lacerate**
        > 100% chance to activate on the second skill (2 second cooldown ⌛️).
        > Deals 80% Physical Damage.
        > Always hits and crits.
        > Applies Laceration to the target for 15 seconds:
        > -10% Dodge
        > -10% Hit Chance
        > -10% Haste
        - <:aqwcheck:1532278320870326382> Finished 'Hit Job' <:queststart:1491012167170920560> at `/join greenguardwest`
        - <:aqwcheck:1532278320870326382> Blacksmith Rep rank 5
        - <:aqwcheck:1532278320870326382> Level 40
        - <:spearaqw:1487000575290642553> Undead Plague Spear (🧟‍♂️Big Jack Sprat, 📍`/join graveyard`)
        - <:swordaqw:1487004634307629056> Kuro's Wrath (🧟‍♂️Kuro, 📍`/join river`)
        - <:axeaqw:1487000523268947988> Massive Horc Cleaver ( <:queststart:1491012167170920560> 'Massive Horc Cleaver', 📍`/join warhorc`)
        - <:swordaqw:1487004634307629056> Sword in the Stone ( <:queststart:1491012167170920560> 'Landing Swords!', 📍`/join greenguardeast`)
        - <:misc:1532256591141929031> Black Knight Orb ( <:queststart:1491012167170920560> 'Hardly Suiting Armor', 📍`/join greenguardwest`)
        - <:axeaqw:1487000523268947988> Forest Axe ( <:queststart:1491012167170920560> 'warm MILK!', 📍`/join greenguardwest`)""")
        )

    @forge.command(
        name="smite", description="Look up Smite Forge Enhancement for Weapon"
    )
    async def smite(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:swordaqw:1487004634307629056>**Smite**
        > 100% chance to activate on the fifth skill (15 second cooldown⌛️).
        > Deals 500% Hybrid Damage.
        - <:aqwcheck:1532278320870326382> Finished 'Star Light, Star Bright' <:queststart:1491012167170920560> at `/join lumafortress`
        - <:aqwcheck:1532278320870326382> Blacksmith Rep rank 6
        - <:aqwcheck:1532278320870326382> Level 60
        - <:misc:1532256591141929031> Death's Power `x3` (🧟‍♂️Death, 📍`/join shadowattack`)
        - <:misc:1532256591141929031> Chaotic Power `x7` (🧟‍♂️Any Lord of Chaos)
        - <:misc:1532256591141929031> Empowered Essence `x50` (🧟‍♂️Almost all monsters at: 📍`/join shadowrealmpast`)
        - <:misc:1532256591141929031> Gem Power `x25` (🧟‍♂️Ultra Battle Gem, 📍`/join undergroundlabb`)
        - <:Tonic:1457810787702935635>Power Tonic `x10` (💰 500k Gold Voucher x2 + 900 Gold, 📍`/join alchemyacademy` -> Fuhu Merge)""")
        )

    @forge.command(
        name="praxis", description="Look up Praxis Forge Enhancement for Weapon"
    )
    async def praxis(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:swordaqw:1487004634307629056> **Praxis**
        > 100% chance to activate on the second skill (4 second cooldown⌛️).
        > Deals 70% Hybrid Damage, increasing by 10% (of original skill damage) on each successive hit to the same target.
        > Applies Spinning Dragon to the target for 2 seconds, reducing the next hit they do to 0.
        > Applies Praxis to the target for 8 seconds:
        > -5% Dodge
        > Praxis prevents Spinning Dragon from applying.
        - <:aqwcheck:1532278320870326382> Finished 'Defeat Jaaku!' <:queststart:1491012167170920560> at `/join shadowfortress`
        - <:aqwcheck:1532278320870326382> Blacksmith Rep rank 6, ChronoSpan Rep rank 10, and Yokai Rep rank 10
        - <:aqwcheck:1532278320870326382> Level 60
        -  <:armoraqw:1487000736087670936> DragonSoul Shinobi *(Armor)* (<:misc:1532256591141929031> Dragon Shinobi Token `x100`, 📍`/join shadowfortress`)
        - <:aqwCape:1501670762174746644> Imperial Chunin Clone (💰 50 000 Gold, 📍`/join dragonkoiz` -> Yokai Rep)
        - <:armoraqw:1487000736087670936> Dragon Rogue (🧟‍♂️Ektorax, 📍`/join ectocave`)
        - <:armoraqw:1487000736087670936> Hashashin Armor (💰 500 000 Gold, 📍`/join yulgar` -> Suggestion Shop)
        - <:armoraqw:1487000736087670936> Thief of Hours Armor (💰 0 Gold, 📍`/join thespan` -> The Span Rep)
        - <:misc:1532256591141929031> Yami `x3` ( <:queststart:1491012167170920560>﻿ 'Embracing Darkness', 📍`/join darkally`)""")
        )

    @forge.command(
        name="acheron", description="Look up Acheron Forge Enhancement for Weapon"
    )
    async def acheron(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:swordaqw:1487004634307629056>**Acheron**
        ❌ This enhancement requires lots of ACs spent on Treasure Keys, or an insane amount of luck. Average spending is around 40 000 ACs.
        > 100% chance to activate on third skill (no cooldown⌛️).
        > Deals 80% Magic Damage to up to 2 targets.
        > Always hits and crits.
        > Applies a stack of Stygian to yourself for every target struck, stacks to 30 and lasts 6 seconds:
        > Gain a rapid DoT based on max health that increases with stacks of Stygian. Other effects do not stack.
        > Stygian prevents Arcane Shield and Safeguard from applying.
        > +30% Damage Boost
        > +30% Hit Chance
        - <:aqwcheck:1532278320870326382> Finished 'Avatar of Fire' <:queststart:1491012167170920560> (Tyndarius) at `/join fireavatar`
        - <:aqwcheck:1532278320870326382> Blacksmith Rep rank 8
        - <:aqwcheck:1532278320870326382> Level 80
        - <:aqwcheck:1532278320870326382> Dark Box & Dark Key for Void Lodestone
        - <:misc:1532256591141929031> Dark Potion `x20` ( <:queststart:1491012167170920560> 'The Dark Box', 📍`/join battleon`)
        - <:misc:1532256591141929031> The Power of Darkness (💰 0 Gold 📍`/join nothing`)
        - <:misc:1532256591141929031> The Mortal Coil (🧟‍♂️ Nulgath, 📍`/join tercessuinotlim`)""")
        )

    @forge.command(
        name="valiance", description="Look up Valiance Forge Enhancement for Weapon"
    )
    async def valiance(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:swordaqw:1487004634307629056> **Valiance**
        > 100% chance to activate on auto attack (15 second cooldown⌛️).
        > Applies Valiance to yourself for 20 seconds:
        > x1.3 Strength
        > x1.3 Intellect
        > x1.3 Dexterity
        > x1.3 Wisdom
        > x1.3 Endurance
        > x1.15 Luck
        - <:aqwcheck:1532278320870326382> Finished 'The Final Challenge' <:queststart:1491012167170920560> (Lord of Order <:classbadge:1471256107057156117>) at `/join battleoff`
        - <:aqwcheck:1532278320870326382> Blacksmith Rep rank 10
        - <:aqwcheck:1532278320870326382> Level 100
        - <:aqwcheck:1532278320870326382> <:armoraqw:1487000736087670936> Fire Champion's Armor (💰 Merge, 📍`/join wartraining`)
        - <:aqwcheck:1532278320870326382> <:classbadge:1471256107057156117> Dragon of Time ( <:queststart:1491012167170920560> 'Hero's Heartbeat', 📍`/join timeinn`)
        - <:aqwcheck:1532278320870326382> <:armoraqw:1487000736087670936> Drakath the Eternal ( <:queststart:1491012167170920560> 'Eternal Drakath Set', 📍`/join eternalchaos`)
        - <:aqwcheck:1532278320870326382> <:swordaqw:1487004634307629056> Eternity Blade ( <:queststart:1491012167170920560> 'Find the Eternity Blade', 📍`/join towerofdoom`)
        - <:misc:1532256591141929031> Gravelyn's DoomFire Token ( <:queststart:1491012167170920560> 'The Summoning ', 📍`/join darkthronehub`)
        - <:armoraqw:1487000736087670936> ArchPaladin's Armor (💰 100 000 Gold, 📍`/join darkthronehub`)""")
        )

    @forge.command(
        name="elysium", description="Look up Elysium Forge Enhancement for Weapon"
    )
    async def elysium(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:swordaqw:1487004634307629056>**Elysium**
        > 100% chance to activate on third skill (no cooldown⌛️).
        > Deals 500 - 2250% Magic Damage to up to 2 targets, increasing the lower your mana is.
        > Cannot crit.
        > Applies a stack of Elysian to yourself for every target struck, stacks to 3 and lasts 8 seconds:
        > Gain a small but rapid HoT that increases with stacks of Elysian. Other effects do not stack.
        > Gain 4 mana per second.
        > +10% Damage Boost
        - <:aqwcheck:1532278320870326382> Finished 'Awe-scention' <:queststart:1491012167170920560> at`/join museum`
        - <:aqwcheck:1532278320870326382> Blacksmith Rep rank 10
        - <:aqwcheck:1532278320870326382> Level 100
        - <:misc:1532256591141929031> Bones from the Void Realm `x20` (💰 50 Void Aura & 50 Bone Dust, 📍`/join shadowfall`)
        - <:misc:1532256591141929031> Blademaster Sword Scroll ( <:queststart:1491012167170920560> 'Legion Sword Training', 📍`/join darkally`)
        - <:misc:1532256591141929031> Archfiend Essence Fragment `x3` ( <:queststart:1491012167170920560> 'Nulgath Demands Work', 📍`/join tercessuinotlim`)
        - <:misc:1532256591141929031> The Divine Will (🧟‍♂️ [Azalith](https://discord.com/channels/1455651278590972019/1484182255101284383), 📍`/join celestialpast`)""")
        )

    @forge.command(
        name="arcanas-concerto",
        description="Look up Arcana's Concerto Forge Enhancement for Weapon",
    )
    async def arcanas_concerto(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:swordaqw:1487004634307629056>**Arcana's Concerto**
        > 50% chance to activate on auto attack (no cooldown⌛️).
        > Deals 50% Hybrid Damage.
        > Applies a stack of Arcana’s Concerto to the target, stacks to 11 and lasts 22 seconds:
        > -2% Physical Resistance
        > -2% Magical Resistance
        - <:aqwcheck:1532278320870326382> Finished '[Darkon, the Conductor](https://discord.com/channels/1455651278590972019/1468338184172736739)' <:queststart:1491012167170920560> at`/join ultradarkon`
        - <:aqwcheck:1532278320870326382> Blacksmith Rep rank 10
        - <:aqwcheck:1532278320870326382> Level 100
        - <:aqwcheck:1532278320870326382> <:spearaqw:1487000575290642553> Prince Darkon's Poleaxe (💰 Merge, 📍`/join ultradrago`)
        - <:aqwcheck:1532278320870326382> <:spearaqw:1487000575290642553> Darkon's Debris 2 (Reconstructed) (💰 Merge, 📍`/join ultradarkon`)
        - <:misc:1532256591141929031> Darkon Insignia `x5` ( <:queststart:1491012167170920560> 'Darkon, the Conductor', 📍`/join ultradarkon`)
        - <:misc:1532256591141929031> King Drago Insignia `x5` ( <:queststart:1491012167170920560> 'Drago, Tyrant of Astravia', 📍`/join ultradrago`)""")
        )

    @forge.command(
        name="ravenous", description="Look up Ravenous Forge Enhancement for Weapon"
    )
    async def ravenous(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:swordaqw:1487004634307629056>**Ravenous**
        > 100% chance to activate on third skill (no cooldown⌛️).
        > Deals 75 - 338% Hybrid Damage, increasing the lower your target's health is.
        > Applies Ravenous to yourself for 10 seconds:
        > +10% Damage Boost
        > +25% Crit Chance
        > Applies a stack of Consumed to your target, stacks to 30 and lasts 10 seconds:
        > -10% Damage Boost, then -1% per additional stack.
        > -10% Crit Chance, then -1% per additional stack.
        - <:aqwcheck:1532278320870326382> Finished The Fiend Shard's Finale <:queststart:1491012167170920560> from Prime Fiend Shard, buy at `/join voidchasm`
        - <:aqwcheck:1532278320870326382> Level 100
        - <:misc:1532256591141929031> Gluttenous Maw (💰 0 Gold, 📍`/house` from Prime Fiend Shard)""")
        )

    @forge.command(
        name="dauntless",
        description="Look up Dauntless Forge Enhancement for Weapon",
    )
    async def dauntless(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:swordaqw:1487004634307629056> **Dauntless**
        > 100% chance to activate on the second skill (3 second cooldown⌛️ ).
        > Deals 190 - 570% Physical Damage, increasing the lower your health is.
        > Lifesteals based on Attack Power, increasing the lower your health is.
        > Always hits and crits.
        > Applies Dauntless to yourself for 12 seconds:
        > +15% Crit Chance
        > +25% Haste
        > -50% Mana Consumption
        > Applies Decay, Cannot Heal to yourself for 6 seconds.
        * <:aqwcheck:1532278320870326382> Must have completed either the <:queststart:1491012167170920560> '[Build Malgor's Armor Set](http://aqwwiki.wikidot.com/tara-s-quests#CradleFarm)' `/join manacradle`
        * <:aqwcheck:1532278320870326382> or the <:queststart:1491012167170920560>  '[Malgor, The First Speaker](http://aqwwiki.wikidot.com/vohu-s-quests)'  at 📍`/join ultraspeaker`
        * <:aqwcheck:1532278320870326382> Must be Level 100.
        * <:aqwcheck:1532278320870326382> Must have Rank 10 Blacksmithing.
        * <:aqwcheck:1532278320870326382> <:armoraqw:1487000736087670936> Infernal Flame Pyromancer (💰 Avatar Tyndarius Insignia `x20` + Fire Avatar's Favor `x75` ,📍 `/join ultratyndarius`)
        * <:aqwcheck:1532278320870326382> <:swordaqw:1487004634307629056> Malgor's ShadowFlame Blade (💰 Malgor Insignia `x20`  Elemental Core `x20`  <:swordaqw:1487004634307629056>ShadowFlame Dragon Blade `x1`, 📍`/join ultraspeaker`)
        * <:aqwcheck:1532278320870326382> <:armoraqw:1487000736087670936> Malgor the ShadowLord ( <:queststart:1491012167170920560> [Build Malgor's Armor Set](http://aqwwiki.wikidot.com/tara-s-quests#CradleFarm) ,📍 `/join manacradle`)
        * <:aqwcheck:1532278320870326382> <:helmaqw:1487000474014974054>  ShadowLord's Helm ( <:queststart:1491012167170920560> [Build Malgor's Armor Set](http://aqwwiki.wikidot.com/tara-s-quests#CradleFarm) ,📍 `/join manacradle`)
        * <:misc:1532256591141929031> Malgor Insignia `x5` ( <:queststart:1491012167170920560> 'Malgor, The First Speaker',📍`/join ultraspeaker`)
        * <:misc:1532256591141929031> Avatar Tyndarius Insignia `x10` ( <:queststart:1491012167170920560> 'Ultra Avatar Tyndarius', 📍 `/join ultratyndarius`)
        """)
        )

    @forge.command(
        name="hearty", description="Look up Hearty Forge Enhancement for Helm"
    )
    async def hearty(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
        <:helmaqw:1487000474014974054> **Hearty**
        > Gives more HP, less of other stats.
        - <:aqwcheck:1532278320870326382> Must have completed the ['The Gaol of Eternal Torment and Misery'](http://aqwwiki.wikidot.com/undead-cashfear-s-quests#GaolCell)
        - <:aqwcheck:1532278320870326382> Rank 7 Grimskull Trolling to purchase these enhancements.
        **Prerequisites:**
        * <:queststart:1491012167170920560> Smite the boulder!:
          * <:aqwcheck:1532278320870326382> Must have Smite (Level 60) in your inventory.
          * ⚡️Boulder Smited `x1` (Click on the blue arrow on Room 2)
         * <:queststart:1491012167170920560> Strike the boulder!:
           * <:aqwcheck:1532278320870326382> Must have completed the previous quest.
           * <:aqwcheck:1532278320870326382> Must have [Scythe of Azalith](http://aqwwiki.wikidot.com/scythe-of-azalith) in your inventory (💰Merge , 📍 `/join infernalarena`)
           * 💥 Boulder Struck (Click on the blue arrow on Room 2)
        * <:queststart:1491012167170920560> Smash the boulder!:
          * <:aqwcheck:1532278320870326382> Must have completed the previous quest.
          * <:aqwcheck:1532278320870326382> Must have J6's Hammer in your inventory. (💰 6 Gold, 📍J6's Secret Hideout Map - 525X, 275Y)
          * 🪨 Boulder Smashed (Click on the blue arrow on Room 2)
        * The Gaol of Eternal Torment and Misery:
          *  ✅ Grimskull's Gaol Cleared""")
        )

    @forge.command(
        name="all_sword", description="Look up all Forge Enhancement for Weapon"
    )
    async def all_sword(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
            <:swordaqw:1487004634307629056>**Smite**
            > 100% chance to activate on the fifth skill (15 second cooldown⌛️).
            > Deals 500% Hybrid Damage.

            <:swordaqw:1487004634307629056> **Praxis**
            > 100% chance to activate on the second skill (4 second cooldown⌛️).
            > Deals 70% Hybrid Damage, increasing by 10% (of original skill damage) on each successive hit to the same target.
            > Applies Spinning Dragon to the target for 2 seconds, reducing the next hit they do to 0.
            > Applies Praxis to the target for 8 seconds:
            > -5% Dodge

            <:swordaqw:1487004634307629056>**Acheron**
            > 100% chance to activate on third skill (no cooldown⌛️).
            > Deals 80% Magic Damage to up to 2 targets.
            > Always hits and crits.
            > Applies a stack of Stygian to yourself for every target struck, stacks to 30 and lasts 6 seconds:
            > Gain a rapid DoT based on max health that increases with stacks of Stygian. Other effects do not stack.
            > Stygian prevents Arcane Shield and Safeguard from applying.
            > +30% Damage Boost
            > +30% Hit Chance

            <:swordaqw:1487004634307629056> **Valiance**
            > 100% chance to activate on auto attack (15 second cooldown⌛️).
            > Applies Valiance to yourself for 20 seconds:
            > x1.3 Strength
            > x1.3 Intellect
            > x1.3 Dexterity
            > x1.3 Wisdom
            > x1.3 Endurance
            > x1.15 Luck

            <:swordaqw:1487004634307629056>**Elysium**
            > 100% chance to activate on third skill (no cooldown⌛️).
            > Deals 500 - 2250% Magic Damage to up to 2 targets, increasing the lower your mana is.
            > Cannot crit.
            > Applies a stack of Elysian to yourself for every target struck, stacks to 3 and lasts 8 seconds:
            > Gain a small but rapid HoT that increases with stacks of Elysian. Other effects do not stack.
            > Gain 4 mana per second.
            > +10% Damage Boost

            <:swordaqw:1487004634307629056>**Arcana's Concerto**
            > 50% chance to activate on auto attack (no cooldown⌛️).
            > Deals 50% Hybrid Damage.
            > Applies a stack of Arcana’s Concerto to the target, stacks to 11 and lasts 22 seconds:
            > -2% Physical Resistance
            > -2% Magical Resistance

            <:swordaqw:1487004634307629056>**Ravenous**
            > 100% chance to activate on third skill (no cooldown⌛️).
            > Deals 75 - 338% Hybrid Damage, increasing the lower your target's health is.
            > Applies Ravenous to yourself for 10 seconds:
            > +10% Damage Boost
            > +25% Crit Chance
            > Applies a stack of Consumed to your target, stacks to 30 and lasts 10 seconds:
            > -10% Damage Boost, then -1% per additional stack.
            > -10% Crit Chance, then -1% per additional stack.

            <:swordaqw:1487004634307629056> **Dauntless**
            > 100% chance to activate on the second skill (3 second cooldown⌛️ ).
            > Deals 190 - 570% Physical Damage, increasing the lower your health is.
            > Lifesteals based on Attack Power, increasing the lower your health is.
            > Always hits and crits.
            > Applies Dauntless to yourself for 12 seconds:
            > +15% Crit Chance
            > +25% Haste
            > -50% Mana Consumption
            > Applies Decay, Cannot Heal to yourself for 6 seconds.
            """)
            )

    @forge.command(
        name="all_cape", description="Look up all Forge Enhancement for Cape"
    )
    async def all_cape(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
            <:aqwCape:1501670762174746644> **Absolution**
            > +50% Healing Boost
            > -20% Physical Boost

            <:aqwCape:1501670762174746644> **Vainglory**
            > +15% Damage Boost
            > -50% Healing Intake

            <:aqwCape:1501670762174746644> **Avarice**
            > +10% Haste
            > -35% Damage Resistance

            <:aqwCape:1501670762174746644> **Penitence**
            > +25% Damage Resistance
            > -25% DoT Boost

            <:aqwCape:1501670762174746644> **Lament**
            > +20% Critical Chance
            > -5% Haste
            """)
            )

    @forge.command(
        name="all_helm", description="Look up all Forge Enhancement for Helm"
    )
    async def all_helm(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            dedent("""\
            <:helmaqw:1487000474014974054> **Vim, Ether**
            > Special passive trait: -33% Mana Consumption

            <:helmaqw:1487000474014974054> **Examen, Ether**
            > Special passive trait: -33% Mana Consumption

            <:helmaqw:1487000474014974054> **Anima, Clairvoyance**
            > Special passive trait: +10% Hit Chance

            <:helmaqw:1487000474014974054> **Penuma, Clairvoyance**
            > Special passive trait: +10% Hit Chance

            <:helmaqw:1487000474014974054> **Hearty**
            > Gives more HP, less of other stats.
            """)
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Forge(bot))
