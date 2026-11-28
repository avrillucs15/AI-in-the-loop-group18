import json
from datetime import datetime, timezone

import aiosqlite
import pytest

from teamsync.db import decisions, summaries
from teamsync.db.connection import init_db


@pytest.mark.asyncio
async def test_save_summary_persists_points_and_status(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)
    decision = await decisions.create_decision(
        1,
        2,
        3,
        "期末專題要做到什麼程度？",
        ["基本要求", "完整 demo"],
        datetime.now(timezone.utc),
    )

    await summaries.save_summary(decision.id, ["時間不足"], "published")

    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT points_json, status, created_at FROM ai_summaries WHERE decision_id = ?",
            (decision.id,),
        )
        row = await cursor.fetchone()

    assert row is not None
    assert json.loads(row[0]) == ["時間不足"]
    assert row[1] == "published"
    assert row[2]


@pytest.mark.asyncio
async def test_save_summary_rejects_unknown_status():
    with pytest.raises(ValueError, match="status must be one of"):
        await summaries.save_summary(1, ["顧慮"], "draft")


@pytest.mark.asyncio
async def test_save_summary_rejects_non_string_points():
    with pytest.raises(ValueError, match="points must contain only strings"):
        await summaries.save_summary(1, ["顧慮", 2], "published")
