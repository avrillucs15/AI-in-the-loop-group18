import discord

from teamsync.db.decisions import get_decision
from teamsync.db.stances import save_stances
from teamsync.models import Stance, StanceType
from teamsync.ui.progress import refresh_progress

STANCE_BUTTON_PREFIX = "stance:"


def make_stance_view(decision_id: int) -> discord.ui.View:
    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="表態", style=discord.ButtonStyle.primary,
                                    custom_id=f"{STANCE_BUTTON_PREFIX}{decision_id}"))
    return view


async def handle_stance_click(interaction: discord.Interaction, decision_id: int) -> None:
    # skeleton：固定存「支持選項 A」。TODO(B, PR 1)：換成立場選單與理由表單
    decision = await get_decision(decision_id)
    if decision is None:
        await interaction.response.send_message("找不到這個決定。", ephemeral=True)
        return
    stance = Stance(user_id=interaction.user.id, option_id=decision.options[0].id, stance=StanceType.SUPPORT)
    await save_stances(decision_id, interaction.user.id, [stance])
    await refresh_progress(interaction.client, decision)
    await interaction.response.send_message("已記錄（skeleton：固定為支持選項 A）", ephemeral=True)
    