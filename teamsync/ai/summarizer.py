import json
import os
from pathlib import Path

from anthropic import APIError, AsyncAnthropic
from dotenv import load_dotenv

from teamsync.models import Concern, Decision, Option, Stance

SYSTEM_PROMPT_PATH = Path(__file__).with_name("system_prompt.md")
ENV_FILE_PATH = Path(__file__).resolve().parents[2] / ".env"


class SummarizerError(Exception):
    pass


async def summarize(question: str, options: list[Option], concerns: list[Concern]) -> list[str]:
    if not concerns:
        return []

    load_dotenv(ENV_FILE_PATH)
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    model = os.getenv("ANTHROPIC_MODEL", "").strip()
    if not api_key:
        raise SummarizerError("ANTHROPIC_API_KEY is not configured.")
    if not model:
        raise SummarizerError("ANTHROPIC_MODEL is not configured.")

    prompt_data = {
        "question": question,
        "options": [{"label": option.label, "text": option.text} for option in options],
        "concerns": [
            {
                "option_label": concern.option_label,
                "stance": concern.stance.value,
                "reason": concern.reason,
            }
            for concern in concerns
        ],
    }

    client = AsyncAnthropic(api_key=api_key)
    try:
        response = await client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"),
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(prompt_data, ensure_ascii=False),
                }
            ],
        )
    except APIError as exc:
        raise SummarizerError("Anthropic API request failed.") from exc
    finally:
        await client.close()

    response_text = "".join(
        block.text for block in response.content if block.type == "text"
    )
    try:
        points = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise SummarizerError("The model response is not valid JSON.") from exc

    if (
        not isinstance(points, list)
        or len(points) > 3
        or any(not isinstance(point, str) or not point.strip() for point in points)
    ):
        raise SummarizerError(
            "The model response must be an array of up to 3 non-empty strings."
        )

    return [point.strip() for point in points]


async def run_summary_flow(bot, decision: Decision, stances: list[Stance]) -> None:
    # TODO(C, PR 2)
    return None