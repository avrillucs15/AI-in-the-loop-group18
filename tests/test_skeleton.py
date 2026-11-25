from datetime import datetime, timezone

from teamsync.db import decisions, stances
from teamsync.db.connection import init_db
from teamsync.models import Stance, StanceType


async def test_decide_then_stance_then_read(tmp_path):
    await init_db(str(tmp_path / "test.db"))
    d = await decisions.create_decision(1, 2, 3, "期末要做到什麼程度？", ["過關就好", "可以 demo"],
                                        datetime.now(timezone.utc))
    assert [o.label for o in d.options] == ["A", "B"]

    await stances.save_stances(d.id, 10, [Stance(10, d.options[0].id, StanceType.SUPPORT)])
    await stances.save_stances(d.id, 10, [Stance(10, d.options[1].id, StanceType.OPPOSE, "想放作品集")])

    rows = await stances.get_stances(d.id)
    assert len(rows) == 1
    assert rows[0].stance is StanceType.OPPOSE
    assert (await decisions.get_decision(d.id)).question == "期末要做到什麼程度？"