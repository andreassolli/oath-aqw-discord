import discord

from firebase_client import db
from ticket_help.tickets.grim_guide import GUIDES

from .role_select import RoleSelect

OPTIONS = {
    "DPS": "CSH, GT, Guardian",
    "Sub DPS": "AF, LC, Arachnomancer",
    "Support": "Lord of Order",
    "Healer": "LH, SC, FB, DMoM, GW",
    "Taunter 1": "Verus DoomKnight",
    "Taunter 2": "Legion Revenant",
    "Tank": "ArchPaladin",
    "Fill": "Cover what is left",
}


class RoleClaimView(discord.ui.View):
    def __init__(
        self,
        ticket_name: str,
        user_id: int,
        parent_view,
        roles: dict[str, str],
        is_requester: bool = False,
    ):
        super().__init__(timeout=60)

        self.ticket_name = ticket_name
        self.user_id = user_id
        self.is_requester = is_requester
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

        if view.selected_role in roles.values():
            return await interaction.response.send_message(
                "That role is already taken.",
                ephemeral=True,
            )

        # add user
        if view.user_id not in claimers and not view.is_requester:
            claimers.append(view.user_id)

        roles[str(view.user_id)] = view.selected_role

        doc_ref.update(
            {
                "claimers": claimers,
                "claimer_roles": roles,
            }
        )

        await view.parent_view._update_ticket_embed(interaction)
        user = interaction.user
        guide_text = GUIDES.get(
            view.selected_role, f"No guide found for {view.selected_role}"
        )

        if view.is_requester:
            await interaction.response.send_message(
                f"""✅ Requester: {user.mention} swapped role to **{view.selected_role}**
            Classes: {OPTIONS.get(view.selected_role)}""",
                ephemeral=False,
            )
        else:
            await interaction.response.send_message(
                f"""✅ {user.mention} claimed as **{view.selected_role}** {len(roles)}/7
            Classes: {OPTIONS.get(view.selected_role)}""",
                ephemeral=False,
            )

        await interaction.followup.send(
            f"{guide_text}",
            ephemeral=True,
        )
