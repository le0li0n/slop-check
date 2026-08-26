#!/usr/bin/env python3
"""PostToolUse hook — flag outward-facing writes that read as AI-written.

The tells + scope live in ai_slop.py (single source of truth, shared with the
pre-commit hook and the /slop-check skill). This file only adapts the hook's
stdin JSON to that scanner.

This hook is a FLAG, not a gate. AI-slop is a judgment call with real false
positives (see the README), so a hit is a place to look. The write stands; exit 2 only routes the report back to
Claude so it gets read before the text goes anywhere.

Loop guard: a given file is reported at most NAG_LIMIT times per session. Past
that, the file is left alone. Repeatedly rewriting prose to satisfy a regex is
how you get text that fails the check and still reads like a chatbot.
"""
import hashlib
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_slop import (  # noqa: E402  -- path set above
    format_report,
    is_outward_path,
    repo_relative,
    scan_file,
)

NAG_LIMIT = 2


def _state_path(session_id):
    safe = hashlib.sha1((session_id or "nosession").encode()).hexdigest()[:16]
    return os.path.join(tempfile.gettempdir(), f"slop-check-{safe}.json")


def _load(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save(path, state):
    try:
        with open(path, "w") as fh:
            json.dump(state, fh)
    except OSError:
        pass  # advisory hook — never fail the turn over a temp file


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)  # unparseable payload — don't interrupt

    path = (data.get("tool_input") or {}).get("file_path", "")
    if not path or not os.path.exists(path) or not is_outward_path(path):
        sys.exit(0)

    try:
        result = scan_file(path)
    except OSError:
        sys.exit(0)
    if not result["flagged"]:
        sys.exit(0)

    rel = repo_relative(path)
    state_path = _state_path(data.get("session_id"))
    state = _load(state_path)
    if state.get(rel, 0) >= NAG_LIMIT:
        sys.exit(0)
    state[rel] = state.get(rel, 0) + 1
    _save(state_path, state)

    print(
        "🤖 This reads as AI-written. Before it goes to anyone:\n\n"
        + format_report(rel, result)
        + "\n\nx = an objective error or a chatbot artifact — fix these."
        "\n. = a signal. Several together are the evidence; one is not."
        "\n\nRead the false-positive rules before cutting: some of these are false"
        "\npositives by design, and a line the writer meant to write stays."
        "\nRewrite the paragraph around its point. Don't patch phrase by phrase.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
