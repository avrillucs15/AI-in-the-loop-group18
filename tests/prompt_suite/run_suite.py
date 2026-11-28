import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from teamsync.ai.summarizer import SummarizerError, summarize
from teamsync.models import Concern, Option, StanceType

CASES_PATH = Path(__file__).with_name("cases.yaml")
DEFAULT_OUTPUT_PATH = Path(__file__).with_name("results") / "latest.json"


def matches_expected_language(points: list[str], expected_language: str | None) -> bool:
    if expected_language is None:
        return True
    if expected_language == "en":
        text = " ".join(points)
        return bool(re.search(r"[A-Za-z]", text)) and not re.search(r"[\u3400-\u9fff]", text)
    raise ValueError(f"Unsupported expected language: {expected_language}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run TeamSync summarizer prompt cases.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path for the JSON results file.",
    )
    return parser.parse_args()


async def run_suite(output_path: Path) -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    suite = yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))
    results = []

    for case in suite["cases"]:
        options = [
            Option(id=index, label=item["label"], text=item["text"])
            for index, item in enumerate(case["options"], start=1)
        ]
        concerns = [
            Concern(
                option_label=item["option_label"],
                stance=StanceType(item["stance"]),
                reason=item["reason"],
            )
            for item in case["concerns"]
        ]

        try:
            points = await summarize(case["question"], options, concerns)
            error = None
        except SummarizerError as exc:
            points = []
            error = str(exc)

        forbidden_hits = [
            phrase
            for phrase in case["must_not"]
            if any(phrase.casefold() in point.casefold() for point in points)
        ]
        count_matches = len(points) == case["expected_count"]
        language_matches = matches_expected_language(
            points, case.get("expected_language")
        )
        passed = error is None and count_matches and not forbidden_hits and language_matches
        results.append(
            {
                "id": case["id"],
                "passed": passed,
                "error": error,
                "points": points,
                "expected_count": case["expected_count"],
                "count_matches": count_matches,
                "expected_language": case.get("expected_language"),
                "language_matches": language_matches,
                "forbidden_hits": forbidden_hits,
                "expected_themes_for_manual_review": case["expected_themes"],
            }
        )

    report = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "model": os.getenv("ANTHROPIC_MODEL", ""),
        "passed": sum(result["passed"] for result in results),
        "total": len(results),
        "cases": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Prompt suite: {report['passed']}/{report['total']} automated checks passed.")
    print(f"Results: {output_path}")
    print("Review each case's expected themes manually; wording is not exact-match tested.")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run_suite(parse_args().output)))
