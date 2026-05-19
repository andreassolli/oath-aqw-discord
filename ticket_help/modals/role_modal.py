import discord

from firebase_client import db
from ticket_help.tickets.utils import set_active_ticket
from ticket_help.utils.claim_generate import generate_claim
from ticket_help.utils.gif_claim import gif_claim

SPEAKER_OPTIONS = {
    "DPS": "CSH, VDK, Guardian ++",
    "Lord of Order": "",
    "Legion Revenant": "",
    "ArchPaladin": "",
    "Fill": "Cover what is left",
}

SPEAKER_ROLE_EMOJIS = {
    "DPS": "⚔️",
    "Lord of Order": "⚖️",
    "Legion Revenant": "💀",
    "ArchPaladin": "🛡️",
    "Fill": "➕",
}

GRIM_OPTIONS = {
    "DPS": "CSH, GT, Guardian",
    "Sub DPS": "AF, LC, Arachnomancer",
    "Support": "Lord of Order",
    "Healer": "LH, SC, FB, DMoM, GW",
    "Taunter 1": "Verus DoomKnight",
    "Taunter 2": "Legion Revenant",
    "Tank": "ArchPaladin",
    "Fill": "Cover what is left",
}

GRIM_ROLE_EMOJIS = {
    "DPS": "⚔️",
    "Sub DPS": "🗡️",
    "Support": "⚖️",
    "Healer": "⛑️",
    "Taunter 1": "📜",
    "Taunter 2": "📜",
    "Tank": "🛡️",
    "Fill": "➕",
}


class RoleModal(discord.ui.Modal, title="Role Selection"):
    def __init__(self, layout, ticket_name: str, roles: dict[str, str], boss: str):
        super().__init__()
        self.layout = layout
        if boss == "Grim":
            options = GRIM_OPTIONS
            role_emojis = GRIM_ROLE_EMOJIS
        else:
            options = SPEAKER_OPTIONS
            role_emojis = SPEAKER_ROLE_EMOJIS

        taken_roles = set(roles.values())

        available = []
        taken = []

        for role, desc in options.items():
            option = discord.SelectOption(
                label=f"{role_emojis.get(role, '❔')} {role}",
                value=role,
                description=desc,
                emoji="🔒" if role in taken_roles and role != "Fill" else None,
            )

            (taken if role in taken_roles else available).append(option)

        options = available + taken
        self.role_selection = discord.ui.Label(
            text="Select a role", component=discord.ui.Select(options=options)
        )
        self.add_item(self.role_selection)
        self.ticket_name = ticket_name

    async def on_submit(self, interaction: discord.Interaction):
        selected_role = self.role_selection.component.values[0]
        doc_ref = db.collection("tickets").document(self.ticket_name)
        # add user
        doc = doc_ref.get()
        data = doc.to_dict() or {}

        claimers = data.get("claimers", [])
        roles = data.get("claimer_roles", {})
        max_claims = data.get("max_claims", 1)
        ticket_name = data.get("ticket_name", "")
        user_id = interaction.user.id
        is_requester = data.get("user_id", False) == user_id

        if not is_requester and user_id not in claimers:
            if len(claimers) >= max_claims:
                return await interaction.response.send_message(
                    "🚫 This ticket is already full.",
                    ephemeral=True,
                )

        if selected_role in roles.values() and selected_role != "Fill":
            return await interaction.response.send_message(
                "That role is already taken.",
                ephemeral=True,
            )

        if user_id not in claimers and not is_requester:
            claimers.append(user_id)

        roles[str(user_id)] = selected_role
        set_active_ticket(interaction.user.id, ticket_name)
        user_ref = db.collection("users").document(str(interaction.user.id))
        user_doc = user_ref.get()
        claim_image = user_doc.to_dict().get("claim_image", None)
        doc_ref.update(
            {
                "claimers": claimers,
                "claimer_roles": roles,
            }
        )
        await self.layout.refresh(interaction)
        await interaction.response.send_message(
            f"You selected: {selected_role}", ephemeral=True
        )
        if interaction.user.display_name == "Proxy" and claim_image is None:
            image = await gif_claim(
                interaction.user.display_name,
                True,
                f"({len(claimers) + 1}/{max_claims + 1})",
                interaction.user,
            )
            await interaction.channel.send(file=discord.File(image, "claim.gif"))
        else:
            image = await generate_claim(
                data.get("aqw_username", interaction.user.display_name),
                True,
                f"({len(claimers) + 1}/{max_claims + 1})",
                interaction.user,
                claim_image,
            )
            await interaction.channel.send(file=discord.File(image, "claim.png"))
        return
