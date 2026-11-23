from __future__ import annotations

from datetime import datetime

import aiosqlite

from teamsync.db.connection import connect, now_iso
from teamsync.models import Decision, Option

LABELS = "ABC"


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


async def get_decision(decision_id: int) -> Decision | None:
    async with connect() as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,))
        row = await cur.fetchone()
        if row is None:
            return None
        cur = await db.execute(
            "SELECT id, label, text FROM options WHERE decision_id = ? ORDER BY label", (decision_id,))
        opts = [Option(id=r["id"], label=r["label"], text=r["text"]) for r in await cur.fetchall()]
    return Decision(id=row["id"], proposer_id=row["proposer_id"], question=row["question"],
                    deadline=datetime.fromisoformat(row["deadline"]), status=row["status"],
                    options=opts, thread_id=row["thread_id"], message_id=row["message_id"])


async def get_by_message(message_id: int) -> Decision | None:
    # TODO(A, PR 1)
    return None


async def set_status(decision_id: int, status: str) -> None:
    # TODO(A, PR 2)
    return None