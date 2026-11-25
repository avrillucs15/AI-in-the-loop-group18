from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
_db_path = "teamsync.db"


async def init_db(path: str) -> None:
    global _db_path
    _db_path = path
    async with aiosqlite.connect(path) as db:
        await db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        await db.commit()


def connect() -> aiosqlite.Connection:
    return aiosqlite.connect(_db_path)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()