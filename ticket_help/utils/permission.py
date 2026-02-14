from ticket_help.commands.admin import has_admin_role


async def is_ticket_owner_or_admin(user, requester_id, interaction):
    if not (user.id == requester_id or has_admin_role(user)):
        await interaction.response.send_message(
            "🚫 Only the ticket owner or an admin can perform this action.",
            ephemeral=True,
        )
        return False
    return True
