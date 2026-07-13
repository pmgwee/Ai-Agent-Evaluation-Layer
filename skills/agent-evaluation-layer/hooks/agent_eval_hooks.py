#!/usr/bin/env python3
"""
agent_eval_hooks.py — Claude Code hook handler for the Agent Evaluation Layer.

Invoked by Claude Code on hook events. Reads the event JSON on stdin and writes
a JSON decision on stdout. Dependency-free (Python 3 standard library only).

Events handled:
  --event session-start
      Injects context at the start of every session: this project uses the
      evaluation layer, where its memory lives, current status, and the rule to
      read/update it. Uses `hookSpecificOutput.additionalContext` (SessionStart
      stdout/context is surfaced to Claude).

  --event stop
      Runs when Claude finishes a turn. If there are uncommitted changes to files
      OUTSIDE `.agent-eval/` but the Evaluation Log was NOT touched, it asks
      Claude (via `decision: block`) to record the iteration before finishing.
      Loop-safe: honors `stop_hook_active`. Never fires on read-only / Q&A turns
      (no working-tree changes) or when git is unavailable.

Kill switch:
  Set environment variable AGENT_EVAL_ENFORCE=off (or 0/false/no) to disable the
  Stop reminder entirely. SessionStart context injection always runs.

Exit code is always 0; control is expressed through the JSON body (Claude Code
only parses hook JSON on exit 0).
"""

import argparse
import json
import os
import re
import subprocess
import sys

EVAL_DIR = ".agent-eval"
LOG_FILE = "EVALUATION_LOG.md"
SPEC_FILE = "SPEC.md"

ENTRY_RE = re.compile(r"^###\s+Entry\s+(\d+)\s+—\s+(\d{4}-\d{2}-\d{2})", re.M)
ENTRY_LOOSE_RE = re.compile(r"^###\s+Entry\s+(\d+)\b", re.M)
OPEN_BACKLOG_RE = re.compile(r"^\s*[-*]\s*\[\s*\]\s+", re.M)


def read_stdin_json():
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def project_root(payload):
    return (
        payload.get("cwd")
        or os.environ.get("CLAUDE_PROJECT_DIR")
        or os.getcwd()
    )


def layer_paths(root):
    d = os.path.join(root, EVAL_DIR)
    return d, os.path.join(d, SPEC_FILE), os.path.join(d, LOG_FILE)


def enforce_disabled():
    return os.environ.get("AGENT_EVAL_ENFORCE", "on").strip().lower() in (
        "off", "0", "false", "no",
    )


def emit(obj):
    sys.stdout.write(json.dumps(obj))
    sys.stdout.flush()
    return 0


def git(root, *args):
    try:
        p = subprocess.run(
            ["git", "-C", root, *args],
            capture_output=True, text=True, timeout=10,
        )
        return p.returncode, p.stdout, p.stderr
    except Exception:
        return 1, "", "git-unavailable"


# ---------------- SessionStart ----------------

def session_start(root):
    eval_dir, spec_path, log_path = layer_paths(root)
    if not os.path.isdir(eval_dir):
        # No layer here — stay silent so we don't nag non-participating repos.
        return emit({})

    initialized = os.path.isfile(spec_path) and os.path.isfile(log_path)
    status = "not fully initialized"
    if initialized:
        try:
            log = open(log_path, encoding="utf-8").read()
        except Exception:
            log = ""
        entries = ENTRY_RE.findall(log)
        n = len(ENTRY_LOOSE_RE.findall(log))
        last = max((d for _, d in entries), default="unknown")
        open_backlog = len(OPEN_BACKLOG_RE.findall(log))
        status = f"{n} iteration entr{'y' if n == 1 else 'ies'}, last {last}, {open_backlog} open backlog item(s)"

    context = (
        "This project uses the Agent Evaluation Layer. Its memory lives in "
        f"`{EVAL_DIR}/` — `{SPEC_FILE}` (rules & rubric) and `{LOG_FILE}` "
        f"(append-only iteration memory). Current status: {status}. "
        "BEFORE doing work, read " + f"`{EVAL_DIR}/{SPEC_FILE}`" + " in full and the "
        "last 2–3 Iteration Log entries. BEFORE finishing this session, run the "
        "Spec's Self-Review Rubric, append a dated Iteration Log entry (what "
        "changed, defects + root cause, lesson learnt, user feedback near-"
        "verbatim, rubric result, next-improvement), update the Open Improvement "
        "Backlog, bump the Spec version if a rule changed, and commit "
        f"`{EVAL_DIR}/`. The Log is append-only — never rewrite past entries."
    )
    return emit({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    })


# ---------------- Stop ----------------

def _norm_path(porcelain_path):
    p = porcelain_path.strip()
    if "->" in p:  # rename: "old -> new"
        p = p.split("->")[-1].strip()
    return p.strip().strip('"')


def stop(root, payload):
    if enforce_disabled():
        return emit({})
    # Avoid infinite loops: if we already blocked and Claude is continuing, let it stop.
    if payload.get("stop_hook_active"):
        return emit({})

    eval_dir, _, _ = layer_paths(root)
    if not os.path.isdir(eval_dir):
        return emit({})

    code, out, _ = git(root, "status", "--porcelain")
    if code != 0:
        return emit({})  # no git / not a repo → don't interfere

    files = [_norm_path(line[3:]) for line in out.splitlines() if line.strip()]
    if not files:
        return emit({})  # clean tree (nothing to log, or already committed)

    def in_eval(f):
        return f == EVAL_DIR or f.startswith(EVAL_DIR + "/") or f.startswith(EVAL_DIR + os.sep)

    def is_layer_admin(f):
        # The layer's own wiring — changing it isn't a product iteration.
        return (
            f == "CLAUDE.md"
            or f.startswith(".claude/")
            or f.startswith(".claude" + os.sep)
        )

    code_changes = [f for f in files if not in_eval(f) and not is_layer_admin(f)]
    log_touched = any(in_eval(f) and f.endswith(LOG_FILE) for f in files)

    if code_changes and not log_touched:
        n = len(code_changes)
        reason = (
            f"Agent Evaluation Layer: this turn changed {n} file(s) but "
            f"`{EVAL_DIR}/{LOG_FILE}` was not updated. Before finishing, run the "
            f"evaluation loop: apply the Self-Review Rubric in `{EVAL_DIR}/{SPEC_FILE}`, "
            "append a dated Iteration Log entry (what changed, defects + root "
            "cause, lesson learnt, user feedback near-verbatim, rubric result, "
            "next-improvement), update the Open Improvement Backlog, bump the Spec "
            f"version if a rule changed, then commit `{EVAL_DIR}/`. "
            "If this turn was not a real iteration (e.g. a question, or WIP), you "
            "may finish without logging. Set AGENT_EVAL_ENFORCE=off to silence this."
        )
        return emit({"decision": "block", "reason": reason})

    return emit({})


def main(argv=None):
    ap = argparse.ArgumentParser(description="Agent Evaluation Layer hook handler.")
    ap.add_argument("--event", required=True,
                    choices=["session-start", "stop"],
                    help="which hook event this invocation handles")
    args = ap.parse_args(argv)

    payload = read_stdin_json()
    root = project_root(payload)

    try:
        if args.event == "session-start":
            return session_start(root)
        if args.event == "stop":
            return stop(root, payload)
    except Exception:
        # Never break the session because of a hook error.
        return emit({})
    return emit({})


if __name__ == "__main__":
    sys.exit(main())
