from teamsync.models import Decision


def build_progress_text(decision: Decision, responder_names: list[str]) -> str:
    # TODO(D, PR 1)
    return "已表態：（stub）"


async def refresh_progress(bot, decision: Decision) -> None:
    # TODO(D, PR 1)：更新首則訊息上的表態人數
    return None