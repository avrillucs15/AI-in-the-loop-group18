from teamsync.models import Concern, Decision, Option, Stance


class SummarizerError(Exception):
    pass


async def summarize(question: str, options: list[Option], concerns: list[Concern]) -> list[str]:
    # TODO(C, PR 1)
    return []


async def run_summary_flow(bot, decision: Decision, stances: list[Stance]) -> None:
    # TODO(C, PR 2)
    return None