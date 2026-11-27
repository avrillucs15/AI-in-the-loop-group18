from datetime import datetime, timedelta, timezone

import pytest

from teamsync.cogs.decide import (
    DEFAULT_DEADLINE, THREAD_NAME_MAX_LEN, format_decision, parse_deadline, parse_options, parse_question,
    thread_name,
)
from teamsync.db import decisions
from teamsync.db.connection import init_db

NOW = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)  # 台灣時間 11/24 20:00


@pytest.fixture
async def decision(tmp_path):
    await init_db(str(tmp_path / "test.db"))
    return await decisions.create_decision(1, 2, 3, "期末要做到什麼程度？", ["過關就好", "可以 demo"],
                                           NOW + DEFAULT_DEADLINE)


# ---------- db/decisions.py ----------

async def test_get_by_message_finds_decision_after_set_message(decision):
    await decisions.set_message(decision.id, 100, 200)
    found = await decisions.get_by_message(200)
    assert found is not None
    assert found.id == decision.id
    assert (found.thread_id, found.message_id) == (100, 200)
    assert [o.text for o in found.options] == ["過關就好", "可以 demo"]


async def test_get_by_message_returns_none_for_unknown_message(decision):
    await decisions.set_message(decision.id, 100, 200)
    assert await decisions.get_by_message(999) is None


async def test_set_status_moves_decision_out_of_open(decision):
    assert decisions.is_open(decision)
    await decisions.set_status(decision.id, decisions.STATUS_REVEALED)
    reloaded = await decisions.get_decision(decision.id)
    assert reloaded.status == "revealed"
    assert not decisions.is_open(reloaded)


async def test_set_status_rejects_unknown_status(decision):
    with pytest.raises(ValueError):
        await decisions.set_status(decision.id, "closed")
    assert (await decisions.get_decision(decision.id)).status == "open"


# ---------- /decide 的輸入驗證 ----------

def test_parse_question_strips_and_rejects_blank():
    assert parse_question("  要不要改用 FastAPI？ ") == "要不要改用 FastAPI？"
    with pytest.raises(ValueError):
        parse_question("   ")


def test_parse_options_skips_empty_optional_field():
    assert parse_options([" 過關就好 ", "可以 demo", ""]) == ["過關就好", "可以 demo"]
    assert parse_options(["A 案", "B 案", None]) == ["A 案", "B 案"]


@pytest.mark.parametrize("raw", [["只有一個", "", ""], ["", "  ", None], ["一樣", "一樣", ""],
                                 ["1", "2", "3", "4"]])
def test_parse_options_rejects_invalid(raw):
    with pytest.raises(ValueError):
        parse_options(raw)


def test_parse_deadline_blank_means_24_hours_later():
    assert parse_deadline("", NOW) == NOW + DEFAULT_DEADLINE
    assert parse_deadline(None, NOW) == NOW + DEFAULT_DEADLINE


def test_parse_deadline_reads_taipei_time_and_returns_utc():
    deadline = parse_deadline("2026-11-25 18:00", NOW)
    assert deadline == datetime(2026, 11, 25, 10, 0, tzinfo=timezone.utc)
    assert deadline.utcoffset() == timedelta(0)


@pytest.mark.parametrize("raw", ["明天", "2026/11/25 18:00", "2026-11-25", "2026-11-24 20:00",
                                 "2026-11-20 09:00"])
def test_parse_deadline_rejects_bad_format_or_past(raw):
    # 最後兩個：剛好等於現在、已經過去
    with pytest.raises(ValueError):
        parse_deadline(raw, NOW)


# ---------- 顯示文字 ----------

async def test_format_decision_shows_options_deadline_and_reveal_hint(decision):
    text = format_decision(decision)
    assert f"決定 #{decision.id}：期末要做到什麼程度？" in text
    assert "A. 過關就好" in text and "B. 可以 demo" in text
    assert f"<t:{int(decision.deadline.timestamp())}:F>" in text
    assert f"/reveal {decision.id}" in text


async def test_thread_name_is_truncated_to_discord_limit(decision):
    decision.question = "很長" * 100
    assert len(thread_name(decision)) == THREAD_NAME_MAX_LEN
    assert thread_name(decision).startswith(f"#{decision.id} ")
