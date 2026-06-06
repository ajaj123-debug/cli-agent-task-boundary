from __future__ import annotations

import json

import cli


def _result(recommendation: str = "TASK BOUNDARY - ok") -> dict:
    return {
        "session": "codex",
        "n_user_prompts": 2,
        "context_tokens_estimate": 10,
        "context_value_score": 0.5,
        "boundary": {
            "decision": "new_task",
            "confidence": 0.9,
            "reasoning": "switch",
            "recommendation": recommendation,
            "scores": {"new_task": 1, "task_complete": 0, "continuation": 0},
        },
    }


def test_watch_source_without_session_path_does_not_stat_none(monkeypatch, capsys):
    calls = {"sleep": 0}
    monkeypatch.setattr(cli, "analyze", lambda session_path, lookback, source: _result())

    def stop_after_first_sleep(seconds: float) -> None:
        calls["sleep"] += 1
        raise KeyboardInterrupt

    monkeypatch.setattr(cli.time, "sleep", stop_after_first_sleep)

    cli.watch(None, lookback=5, json_out=True, color=False, source="codex")

    assert calls["sleep"] == 1
    assert json.loads(capsys.readouterr().out.splitlines()[0])["session"] == "codex"


def test_json_output_is_ascii_safe(monkeypatch, capsys):
    monkeypatch.setattr(cli, "analyze", lambda session_path, lookback, source: _result("emoji ⚡ ok"))
    monkeypatch.setattr(cli.sys, "argv", ["cli.py", "--source", "codex", "--json"])

    assert cli.main() == 0

    output = capsys.readouterr().out
    assert "⚡" not in output
    assert "\\u26a1" in output
