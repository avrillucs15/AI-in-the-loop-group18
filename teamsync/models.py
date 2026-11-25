from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class StanceType(str, Enum):
    SUPPORT = "support"
    RESERVED = "reserved"
    OPPOSE = "oppose"


@dataclass
class Option:
    id: int
    label: str
    text: str


@dataclass
class Decision:
    id: int
    proposer_id: int
    question: str
    deadline: datetime
    status: str
    options: list[Option] = field(default_factory=list)
    thread_id: int | None = None
    message_id: int | None = None


@dataclass
class Stance:
    user_id: int
    option_id: int
    stance: StanceType
    reason: str | None = None
    anonymous: bool = True


@dataclass
class Concern:
    option_label: str
    stance: StanceType
    reason: str