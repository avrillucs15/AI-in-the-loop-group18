from __future__ import annotations

from datetime import datetime

import aiosqlite

from teamsync.db.connection import connect, now_iso
from teamsync.models import Decision, Option

LABELS = "ABC"

# 決定的狀態只會往前走：open → revealed → concluded
STATUS_OPEN = "open"
STATUS_REVEALED = "revealed"
STATUS_CONCLUDED = "concluded"
VALID_STATUSES = (STATUS_OPEN, STATUS_REVEALED, STATUS_CONCLUDED)

CLOSED_MESSAGE = "這個決定已經揭曉，不能再表態。"


async def create_decision(guild_id: int, channel_id: int, proposer_id: int, question: str,
                          options: list[str], deadline: datetime) -> Decision:
    async with connect() as db:
        cur = await db.execute(
            "INSERT INTO decisions (guild_id, channel_id, proposer_id, question, deadline, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (guild_id, channel_id, proposer_id, question, deadline.isoformat(), now_iso()),
        )
        decision_id = cur.lastrowid
        opts = []
        for label, text in zip(LABELS, options):
            cur = await db.execute(
                "INSERT INTO options (decision_id, label, text) VALUES (?, ?, ?)",
                (decision_id, label, text),
            )
            opts.append(Option(id=cur.lastrowid, label=label, text=text))
        await db.commit()
    return Decision(id=decision_id, proposer_id=proposer_id, question=question,
                    deadline=deadline, status="open", options=opts)


async def set_message(decision_id: int, thread_id: int | None, message_id: int) -> None:
    async with connect() as db:
        await db.execute("UPDATE decisions SET thread_id = ?, message_id = ? WHERE id = ?",
                         (thread_id, message_id, decision_id))
        await db.commit()


async def _load(db: aiosqlite.Connection, where: str, value: int) -> Decision | None:
    assert where in ("id", "message_id")  # 欄位名稱只來自程式內的常數，不接受外部輸入
    db.row_factory = aiosqlite.Row
    cur = await db.execute(f"SELECT * FROM decisions WHERE {where} = ?", (value,))
    row = await cur.fetchone()
    if row is None:
        return None
    cur = await db.execute(
        "SELECT id, label, text FROM options WHERE decision_id = ? ORDER BY label", (row["id"],))
    opts = [Option(id=r["id"], label=r["label"], text=r["text"]) for r in await cur.fetchall()]
    return Decision(id=row["id"], proposer_id=row["proposer_id"], question=row["question"],
                    deadline=datetime.fromisoformat(row["deadline"]), status=row["status"],
                    options=opts, thread_id=row["thread_id"], message_id=row["message_id"])


async def get_decision(decision_id: int) -> Decision | None:
    async with connect() as db:
        return await _load(db, "id", decision_id)


async def get_by_message(message_id: int) -> Decision | None:
    """用討論串首則訊息（放按鈕與表態人數的那則）找回決定。"""
    async with connect() as db:
        return await _load(db, "message_id", message_id)


async def set_status(decision_id: int, status: str) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"未知的狀態：{status!r}（只能是 {', '.join(VALID_STATUSES)}）")
    async with connect() as db:
        await db.execute("UPDATE decisions SET status = ? WHERE id = ?", (status, decision_id))
        await db.commit()


def is_open(decision: Decision) -> bool:
    """還能不能表態。B 的表態按鈕與表單送出時都要呼叫；False 時回覆 CLOSED_MESSAGE。"""
    return decision.status == STATUS_OPEN
