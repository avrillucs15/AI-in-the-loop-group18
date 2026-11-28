# TeamSync AI prompt card

## Purpose

After a team decision is revealed, summarize the concrete concerns and expectations members wrote in reserved or opposing stances. The summary is a reading aid, not a vote, recommendation, or final decision.

## Model and prompt

- Provider: Anthropic Messages API.
- Model: read from `ANTHROPIC_MODEL`; the latest recorded prompt-suite run used `claude-haiku-5-5`.
- System prompt: [`teamsync/ai/system_prompt.md`](../teamsync/ai/system_prompt.md).
- Implementation: [`teamsync/ai/summarizer.py`](../teamsync/ai/summarizer.py), `summarize()`.

## Input and output

The request contains:

- The decision question.
- Each option's label and text.
- Each concern's option label, stance (`reserved` or `oppose`), and written reason.

Discord user IDs and names are not fields in the request payload. However, a member could include identifying information in their free-text reason; that text is sent to the API, and the prompt asks the model not to repeat identifying details in its summary. Avoid sending sensitive real-world details during testing.

The model must return only a JSON array of zero to three non-empty strings. Similar reasons about the same core concern should be combined; distinct concerns should remain separate. Empty or non-substantive input should produce `[]`. The summarizer rejects malformed JSON and invalid output shape with `SummarizerError`.

## Human control and current status

The AI only summarizes concerns that have already been stated. It must not infer who holds a view, invent reasons, recommend an option, or make the final decision.

The summarizer and summary persistence are implemented. The planned Discord workflow—calling the summarizer after `/reveal`, privately asking the proposer whether to publish, and publishing only after approval—is not yet implemented; `run_summary_flow()` remains a stub. Therefore, the current 10-case result evaluates the summarizer directly, not the end-to-end Discord experience.

## Evaluation

Prompt cases: [`tests/prompt_suite/cases.yaml`](../tests/prompt_suite/cases.yaml)  
Runner: [`tests/prompt_suite/run_suite.py`](../tests/prompt_suite/run_suite.py)  
Latest result: [`tests/prompt_suite/results/latest.json`](../tests/prompt_suite/results/latest.json)

The latest recorded run used `claude-haiku-5-5` at `2026-11-28 10:46:21 UTC` and passed **10/10 automated checks**. The suite covers overlapping and distinct concerns, different stances, empty and vague input, instruction-like text, identifying details, uncertainty, and mixed-language technical feedback.

Automated checks cover API/response errors, expected point counts, forbidden phrases, and an English-script check for the English-language case. Expected themes are not semantically graded: review the generated points manually. This is a small, hand-written suite, not evidence from real users, and model output can vary between runs.

Run the prompt suite from the repository root with `python tests/prompt_suite/run_suite.py`. It sends the test prompt and synthetic cases to the configured Anthropic model and may incur API charges.
