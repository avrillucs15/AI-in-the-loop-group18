from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

from teamsync.db import decisions, stances
from teamsync.ui.stance_form import STANCE_BUTTON_PREFIX, handle_stance_click, make_stance_view


class DecideCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="decide", description="發起一個需要大家表態的決定")
    @app_commands.describe(content="格式：問題 | 選項A | 選項B（| 選項C）")
    async def decide(self, interaction: discord.Interaction, content: str):
        parts = [p.strip() for p in content.split("|") if p.strip()]
        if len(parts) < 3:
            await interaction.response.send_message("格式：問題 | 選項A | 選項B（| 選項C）", ephemeral=True)
            return
        question, options = parts[0], parts[1:4]
        deadline = datetime.now(timezone.utc) + timedelta(hours=24)
        decision = await decisions.create_decision(
            interaction.guild_id, interaction.channel_id, interaction.user.id, question, options, deadline)
        lines = [f"**決定 #{decision.id}：{question}**"] + [f"{o.label}. {o.text}" for o in decision.options]
        await interaction.response.send_message("\n".join(lines), view=make_stance_view(decision.id))
        message = await interaction.original_response()
        await decisions.set_message(decision.id, None, message.id)

    @app_commands.command(name="reveal", description="揭曉所有人的表態")
    @app_commands.describe(decision_id="決定編號（# 後面的數字）")
    async def reveal(self, interaction: discord.Interaction, decision_id: int):
        # skeleton：原樣印出資料。TODO(A, PR 2)：限提議者、改狀態、換成 B 的 embed 與 C 的 AI 流程
        decision = await decisions.get_decision(decision_id)
        if decision is None:
            await interaction.response.send_message("找不到這個決定。", ephemeral=True)
            return
        rows = await stances.get_stances(decision_id)
        labels = {o.id: o.label for o in decision.options}
        lines = [f"**決定 #{decision.id} 原始資料：{decision.question}**"]
        lines += [f"<@{s.user_id}>｜{labels[s.option_id]}｜{s.stance.value}｜{s.reason or '-'}" for s in rows]
        if not rows:
            lines.append("（還沒有人表態）")
        await interaction.response.send_message("\n".join(lines),
                                                allowed_mentions=discord.AllowedMentions.none())

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type is not discord.InteractionType.component:
            return
        custom_id = (interaction.data or {}).get("custom_id", "")
        if custom_id.startswith(STANCE_BUTTON_PREFIX):
            await handle_stance_click(interaction, int(custom_id[len(STANCE_BUTTON_PREFIX):]))


async def setup(bot: commands.Bot):
    await bot.add_cog(DecideCog(bot))
