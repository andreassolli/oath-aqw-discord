from config import HELPER_ROLE_ID, ADMIN_ROLE_ID, OATHSWORN_ROLE_ID
from firebase_client import db

def get_overwrites(interaction: discord.Interaction):
    guild = interaction.guild

    base_member_perms = dict(
        view_channel=True,
        send_messages=True,
        read_message_history=True,
        mention_everyone=False,
    )

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),

        interaction.user: discord.PermissionOverwrite(**base_member_perms),

        guild.me: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            mention_everyone=True,
        ),
    }

    role_configs = {
        HELPER_ROLE_ID: base_member_perms,
        OATHSWORN_ROLE_ID: {
            **base_member_perms,
            "mention_everyone": True,
        },
        ADMIN_ROLE_ID: {
            **base_member_perms,
            "mention_everyone": True,
            "manage_channels": True,
        },
    }

    for role_id, perms in role_configs.items():
        role = guild.get_role(role_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(**perms)

    return overwrites

def can_claim_ticket(claimers, max_claims, interaction, requester_id):
    if len(claimers) >= self.max_claims:
        return await interaction.followup.send(
            "🚫 No more spots available.", ephemeral=True
        )

    user_ref = db.collection("users").document(str(interaction.user.id))
    user_doc = user_ref.get()

    if user_doc.exists and user_doc.to_dict().get("active_ticket"):
        return await interaction.followup.send(
            "🚫 You are already helping on another ticket.",
            ephemeral=True
        )

    if interaction.user.id == requester_id:
        return await interaction.followup.send(
            "🚫 Ticket creator cannot claim their own ticket.",
            ephemeral=True,
        )

    if not has_helper_role(interaction):
        return await interaction.followup.send(
            "🚫 You are not a helper, become one to claim or unclaim tickets.",
            ephemeral=True,
        )
