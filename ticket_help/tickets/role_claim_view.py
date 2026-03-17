import discord

from firebase_client import db

from .role_select import RoleSelect


class RoleClaimView(discord.ui.View):
    def __init__(
        self, ticket_name: str, user_id: int, parent_view, roles: dict[str, str]
    ):
        super().__init__(timeout=60)

        self.ticket_name = ticket_name
        self.user_id = user_id
        self.parent_view = parent_view
        self.selected_role: str | None = None

        self.add_item(RoleSelect(roles))
        self.add_item(ConfirmRoleButton())


class ConfirmRoleButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Confirm Role", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        view: RoleClaimView = self.view

        if not view.selected_role:
            return await interaction.response.send_message(
                "Select a role first.",
                ephemeral=True,
            )

        doc_ref = db.collection("tickets").document(view.ticket_name)
        doc = doc_ref.get()
        data = doc.to_dict() or {}

        claimers = data.get("claimers", [])
        roles = data.get("claimer_roles", {})

        # ✅ FIX: check AFTER roles is loaded
        if view.selected_role in roles.values():
            return await interaction.response.send_message(
                "That role is already taken.",
                ephemeral=True,
            )

        # add user
        if view.user_id not in claimers:
            claimers.append(view.user_id)

        roles[str(view.user_id)] = view.selected_role

        doc_ref.update(
            {
                "claimers": claimers,
                "claimer_roles": roles,
            }
        )

        await view.parent_view._update_ticket_embed(interaction)

        await interaction.response.send_message(
            f"✅ You claimed as **{view.selected_role}**",
            ephemeral=True,
        )
