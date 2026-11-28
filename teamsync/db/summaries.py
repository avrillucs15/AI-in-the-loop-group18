import json

from teamsync.db.connection import connect, now_iso

VALID_STATUSES = {"published", "discarded", "failed"}


async def save_summary(decision_id: int, points: list[str], status: str) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(sorted(VALID_STATUSES))}")
    if any(not isinstance(point, str) for point in points):
        raise ValueError("points must contain only strings")

    async with connect() as db:
        await db.execute(
            "INSERT INTO ai_summaries (decision_id, points_json, status, created_at)"
            " VALUES (?, ?, ?, ?)",
            (decision_id, json.dumps(points, ensure_ascii=False), status, now_iso()),
        )
        await db.commit()