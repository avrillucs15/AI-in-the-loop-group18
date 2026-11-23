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

    # 第 6 輪把 /reveal 加在這裡

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type is not discord.InteractionType.component:
            return
        custom_id = (interaction.data or {}).get("custom_id", "")
        if custom_id.startswith(STANCE_BUTTON_PREFIX):
            await handle_stance_click(interaction, int(custom_id[len(STANCE_BUTTON_PREFIX):]))


async def setup(bot: commands.Bot):
    await bot.add_cog(DecideCog(bot))
