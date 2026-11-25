from __future__ import annotations

from teamsync.db.connection import connect, now_iso
from teamsync.models import Stance, StanceType


async def save_stances(decision_id: int, user_id: int, stances: list[Stance]) -> None:
    """覆蓋這個人在這個決定的所有舊表態。"""
    async with connect() as db:
        await db.execute("DELETE FROM stances WHERE decision_id = ? AND user_id = ?",
                         (decision_id, user_id))
        for s in stances:
            await db.execute(
                "INSERT INTO stances (decision_id, user_id, option_id, stance, reason, anonymous, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (decision_id, user_id, s.option_id, s.stance.value, s.reason, int(s.anonymous), now_iso()),
            )
        await db.commit()


async def get_stances(decision_id: int) -> list[Stance]:
    async with connect() as db:
        cur = await db.execute(
            "SELECT user_id, option_id, stance, reason, anonymous FROM stances"
            " WHERE decision_id = ? ORDER BY updated_at",
            (decision_id,),
        )
        rows = await cur.fetchall()
    return [Stance(user_id=r[0], option_id=r[1], stance=StanceType(r[2]), reason=r[3], anonymous=bool(r[4]))
            for r in rows]


async def get_responder_ids(decision_id: int) -> list[int]:
    # TODO(B, PR 1)
    return []