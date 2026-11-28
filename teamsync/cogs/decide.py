from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

from teamsync.db import decisions, stances
from teamsync.models import Decision
from teamsync.ui.progress import build_progress_text
from teamsync.ui.stance_form import STANCE_BUTTON_PREFIX, handle_stance_click, make_stance_view

TAIPEI = timezone(timedelta(hours=8), "Asia/Taipei")
DEADLINE_FORMAT = "%Y-%m-%d %H:%M"
DEFAULT_DEADLINE = timedelta(hours=24)
MAX_OPTIONS = 3              # Discord 一則訊息最多 5 列元件，B 的表態表單每個選項佔一列
QUESTION_MAX_LEN = 200
OPTION_MAX_LEN = 80          # B 的立場選單會顯示選項文字，Discord 選單標籤上限 100 字
THREAD_NAME_MAX_LEN = 100    # Discord 討論串名稱上限
THREAD_ARCHIVE_MINUTES = 10080  # 7 天；決定可能開好幾天，避免討論串提早封存


# ---------- 純函式：輸入驗證與文字（tests/test_decisions.py 測這些） ----------

def parse_question(raw: str | None) -> str:
    question = (raw or "").strip()
    if not question:
        raise ValueError("問題不能空白。")
    return question


def parse_options(raw: list[str | None]) -> list[str]:
    """去掉空白欄位後要剩 2–3 個、且不重複的選項。"""
    options = [o.strip() for o in raw if o and o.strip()]
    if len(options) < 2:
        raise ValueError("至少要填 2 個選項。")
    if len(options) > MAX_OPTIONS:
        raise ValueError(f"最多 {MAX_OPTIONS} 個選項。")
    if len(set(options)) != len(options):
        raise ValueError("選項不能重複。")
    return options


def parse_deadline(raw: str | None, now: datetime) -> datetime:
    """留空 = 24 小時後；否則以台灣時間解析 YYYY-MM-DD HH:MM。回傳 UTC 時間。期限只顯示，不會自動揭曉。"""
    text = (raw or "").strip()
    if not text:
        return now + DEFAULT_DEADLINE
    try:
        deadline = datetime.strptime(text, DEADLINE_FORMAT).replace(tzinfo=TAIPEI)
    except ValueError:
        raise ValueError("期限格式須為 YYYY-MM-DD HH:MM，或留空表示 24 小時後。") from None
    if deadline <= now:
        raise ValueError("期限必須晚於現在。")
    return deadline.astimezone(timezone.utc)


def format_decision(decision: Decision) -> str:
    ts = int(decision.deadline.timestamp())
    lines = [f"**決定 #{decision.id}：{decision.question}**"]
    lines += [f"{o.label}. {o.text}" for o in decision.options]
    lines.append(f"期限：<t:{ts}:F>（<t:{ts}:R>）")
    lines.append(f"到期不會自動揭曉，請提議者 <@{decision.proposer_id}> 用 `/reveal {decision.id}` 揭曉。")
    lines.append("請到討論串按「表態」，揭曉前只有你自己看得到內容。")
    return "\n".join(lines)


def thread_name(decision: Decision) -> str:
    return f"#{decision.id} {decision.question}"[:THREAD_NAME_MAX_LEN]


# ---------- /decide 的表單與流程 ----------

class DecideModal(discord.ui.Modal, title="發起決定"):
    # Discord 表單最多 5 個欄位：問題 + 3 個選項 + 期限，剛好用滿
    question = discord.ui.TextInput(label="問題", style=discord.TextStyle.paragraph,
                                    max_length=QUESTION_MAX_LEN)
    option_a = discord.ui.TextInput(label="選項 A", max_length=OPTION_MAX_LEN)
    option_b = discord.ui.TextInput(label="選項 B", max_length=OPTION_MAX_LEN)
    option_c = discord.ui.TextInput(label="選項 C（選填）", max_length=OPTION_MAX_LEN, required=False)
    deadline = discord.ui.TextInput(label="期限（台灣時間，選填）", required=False, max_length=16,
                                    placeholder="YYYY-MM-DD HH:MM；留空 = 24 小時後")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            question = parse_question(self.question.value)
            options = parse_options([self.option_a.value, self.option_b.value, self.option_c.value])
            deadline = parse_deadline(self.deadline.value, datetime.now(timezone.utc))
        except ValueError as e:
            await interaction.response.send_message(f"{e} 請重新輸入 `/decide`。", ephemeral=True)
            return
        await post_decision(interaction, question, options, deadline)


async def post_decision(interaction: discord.Interaction, question: str, options: list[str],
                        deadline: datetime) -> None:
    """存決定 → 頻道發摘要 → 開討論串 → 討論串首則訊息（表態人數 + 表態按鈕）→ set_message()"""
    decision = await decisions.create_decision(
        interaction.guild_id, interaction.channel_id, interaction.user.id, question, options, deadline)
    text = format_decision(decision)
    no_ping = discord.AllowedMentions.none()
    await interaction.response.send_message(text, allowed_mentions=no_ping)
    summary = await interaction.original_response()
    progress = build_progress_text(decision, [])
    try:
        thread = await summary.create_thread(name=thread_name(decision),
                                             auto_archive_duration=THREAD_ARCHIVE_MINUTES)
        first = await thread.send(progress, view=make_stance_view(decision.id), allowed_mentions=no_ping)
        await decisions.set_message(decision.id, thread.id, first.id)
    except discord.HTTPException:
        # 開不了討論串（多半是 bot 缺「建立公開討論串」權限）時，把按鈕放回頻道訊息，至少還能表態
        await summary.edit(content=f"{text}\n\n{progress}", view=make_stance_view(decision.id),
                           allowed_mentions=no_ping)
        await decisions.set_message(decision.id, None, summary.id)
        await interaction.followup.send(
            "無法開討論串（bot 可能缺少「建立公開討論串」權限），表態按鈕改放在這則訊息上。", ephemeral=True)


class DecideCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="decide", description="發起一個需要大家表態的決定（會跳出表單）")
    @app_commands.guild_only()
    async def decide(self, interaction: discord.Interaction):
        if isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("請在一般文字頻道使用 `/decide`，討論串裡不能再開討論串。",
                                                    ephemeral=True)
            return
        await interaction.response.send_modal(DecideModal())

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
