import discord

from teamsync.models import Decision, Stance, StanceType


def tally(decision: Decision, stances: list[Stance]) -> dict[int, dict[StanceType, int]]:
    # TODO(B, PR 2)
    return {}


def build_reveal_embed(decision: Decision, stances: list[Stance], names: dict[int, str]) -> discord.Embed:
    # TODO(B, PR 2)
    return discord.Embed(title=f"揭曉（stub）：{decision.question}")