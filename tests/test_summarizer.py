import json
from types import SimpleNamespace

import pytest

from teamsync.ai import summarizer
from teamsync.models import Concern, Option, StanceType


class FakeClient:
    def __init__(self, response_text=None, error=None):
        self.response_text = response_text
        self.error = error
        self.request = None
        self.closed = False
        self.messages = self

    async def create(self, **kwargs):
        self.request = kwargs
        if self.error is not None:
            raise self.error
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=self.response_text)]
        )

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_summarize_sends_only_decision_and_concern_data(monkeypatch):
    client = FakeClient('["時程不足可能影響核心功能完成"]')
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "test-model")
    monkeypatch.setattr(summarizer, "AsyncAnthropic", lambda api_key: client)

    points = await summarizer.summarize(
        "期末專題要做到什麼程度？",
        [Option(id=1, label="A", text="基本要求")],
        [
            Concern(
                option_label="A",
                stance=StanceType.OPPOSE,
                reason="時間不夠完成核心功能",
            )
        ],
    )

    payload = json.loads(client.request["messages"][0]["content"])
    assert points == ["時程不足可能影響核心功能完成"]
    assert payload == {
        "question": "期末專題要做到什麼程度？",
        "options": [{"label": "A", "text": "基本要求"}],
        "concerns": [
            {
                "option_label": "A",
                "stance": "oppose",
                "reason": "時間不夠完成核心功能",
            }
        ],
    }
    assert "user_id" not in client.request["messages"][0]["content"]
    assert client.closed


@pytest.mark.asyncio
async def test_summarize_returns_empty_without_api_call(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)

    assert await summarizer.summarize("問題", [], []) == []


@pytest.mark.asyncio
async def test_summarize_requires_api_configuration(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "")
    monkeypatch.setattr(
        summarizer,
        "AsyncAnthropic",
        lambda api_key: pytest.fail("API client must not be constructed"),
    )

    with pytest.raises(summarizer.SummarizerError, match="ANTHROPIC_MODEL"):
        await summarizer.summarize(
            "問題",
            [],
            [Concern(option_label="A", stance=StanceType.OPPOSE, reason="顧慮")],
        )


@pytest.mark.asyncio
async def test_summarize_wraps_anthropic_api_errors(monkeypatch):
    from anthropic import APIError

    client = FakeClient(
        error=APIError("request failed", request=SimpleNamespace(), body=None)
    )
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "test-model")
    monkeypatch.setattr(summarizer, "AsyncAnthropic", lambda api_key: client)

    with pytest.raises(summarizer.SummarizerError, match="API request failed"):
        await summarizer.summarize(
            "問題",
            [],
            [Concern(option_label="A", stance=StanceType.OPPOSE, reason="顧慮")],
        )

    assert client.closed


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response_text",
    [
        "not json",
        '{"point": "not an array"}',
        '["", "另一點"]',
        '["一", "二", "三", "四"]',
    ],
)
async def test_summarize_rejects_invalid_model_responses(monkeypatch, response_text):
    client = FakeClient(response_text)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "test-model")
    monkeypatch.setattr(summarizer, "AsyncAnthropic", lambda api_key: client)

    with pytest.raises(summarizer.SummarizerError):
        await summarizer.summarize(
            "問題",
            [],
            [Concern(option_label="A", stance=StanceType.OPPOSE, reason="顧慮")],
        )

    assert client.closed
