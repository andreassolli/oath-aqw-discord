import discord

from firebase_client import db
from user_verification.user_join import DidUserJoinView
from user_verification.utils import build_join_ticket_embed


async def restore_join_tickets(bot: discord.Client):

    docs = db.collection("join_tickets").stream()

    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue

        try:
            channel = await bot.fetch_channel(int(data["channel_id"]))
            if not isinstance(channel, discord.TextChannel):
                print(
                    f"Channel {channel.id} is not a text channel. Skipping ticket for Discord ID {data['discord_id']}."
                )
                continue
        except discord.NotFound:
            print(f"Channel {data['channel_id']} truly does not exist.")
            continue
        except discord.Forbidden:
            print(f"No permission to access channel {data['channel_id']}.")
            continue

        try:
            message = await channel.fetch_message(int(data["message_id"]))
        except discord.NotFound:
            print(
                f"Message with ID {data['message_id']} not found in channel {channel.id}. Skipping ticket for Discord ID {data['discord_id']}."
            )
            continue

        print(
            "Restoring join ticket for Discord ID {data['discord_id']} in channel {channel.id}."
        )
        embed = build_join_ticket_embed(
            guild=channel.guild,
            discord_id=data["discord_id"],
            ign=data["ign"],
            created_at=data.get("created_at"),
        )

        view = DidUserJoinView(
            discord_id=data["discord_id"],
            ign=data["ign"],
        )

        await message.edit(embed=embed, view=view)
