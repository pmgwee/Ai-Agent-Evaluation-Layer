#!/usr/bin/env python3
"""
probe.py — scaffolder & health check for the Agent Evaluation Layer.

Dependency-free (Python 3 standard library only). Installs nothing: the skill is
invoked by typing `/agent-evaluation-layer` (its folder name in .claude/skills/), so there is no
command file to install. This script only scaffolds or inspects a project's log.

The layer is manual and maintains ONE file, .agent-eval/EVALUATION_LOG.md. It is
not a rules file and never edits the project's own docs or installs hooks.

Modes:
    python probe.py --dir /path/to/project            # health report
    python probe.py --init --dir /path/to/project     # scaffold the log file only
    python probe.py --dir /path/to/project --json     # machine-readable report
    python probe.py --dir /path/to/project --strict   # warnings -> non-zero exit

Exit codes:
    0  healthy / action ok
    1  not initialized, or missing required file/sections (hard failure)
    2  healthy structure but warnings present, and --strict was set
"""

import argparse
import json
import os
import re
import sys
from datetime import date, datetime

EVAL_DIR = ".agent-eval"
LOG_FILE = "EVALUATION_LOG.md"

LOG_REQUIRED = [
    ("How to use", r"^#+\s*.*how to use this file"),
    ("Decisions & Rules History", r"^#+\s*.*decisions.*history"),
    ("Open Improvement Backlog", r"^#+\s*.*open improvement backlog"),
    ("Iteration Log", r"^#+\s*.*iteration log"),
]

ENTRY_RE = re.compile(r"^###\s+Entry\s+(\d+)\s+—\s+(\d{4}-\d{2}-\d{2})", re.M | re.I)
ENTRY_RE_LOOSE = re.compile(r"^###\s+Entry\s+(\d+)\b", re.M | re.I)
OPEN_BACKLOG_RE = re.compile(r"^\s*[-*]\s*\[\s*\]\s+", re.M)
DONE_BACKLOG_RE = re.compile(r"^\s*[-*]\s*\[[xX]\]\s+", re.M)


def find_layer(start):
    cur = os.path.abspath(start)
    while True:
        candidate = os.path.join(cur, EVAL_DIR)
        if os.path.isdir(candidate):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def check_sections(text, required):
    present, missing = [], []
    for label, pattern in required:
        if re.search(pattern, text, re.M | re.I):
            present.append(label)
        else:
            missing.append(label)
    return present, missing


def probe(project_dir):
    report = {
        "project_dir": os.path.abspath(project_dir),
        "eval_dir": None,
        "initialized": False,
        "errors": [],
        "warnings": [],
        "info": {},
    }

    root = find_layer(project_dir)
    if root is None:
        report["errors"].append(
            f"No {EVAL_DIR}/ found in {os.path.abspath(project_dir)} or any parent. "
            f"Run `/agent-evaluation-layer` in Claude Code (or `probe.py --init`) to create one."
        )
        return report

    report["project_dir"] = root
    eval_dir = os.path.join(root, EVAL_DIR)
    report["eval_dir"] = eval_dir
    report["initialized"] = True

    log_path = os.path.join(eval_dir, LOG_FILE)

    if not os.path.isfile(log_path):
        report["errors"].append(f"Missing {EVAL_DIR}/{LOG_FILE}")
    if report["errors"]:
        return report

    log = read(log_path)

    _, log_missing = check_sections(log, LOG_REQUIRED)
    for m in log_missing:
        report["errors"].append(f"{LOG_FILE} is missing required section: {m}")

    entries = ENTRY_RE.findall(log)
    loose = ENTRY_RE_LOOSE.findall(log)
    report["info"]["iteration_entries"] = len(loose)
    if loose and not entries:
        report["warnings"].append(
            "Iteration entries found but none match the dated format "
            "'### Entry <N> — YYYY-MM-DD'. Dates keep the log searchable."
        )
    if not loose:
        report["warnings"].append(
            "No Iteration Log entries yet. Add Entry 1 (bootstrap) so the memory has a starting point."
        )

    if entries:
        nums = [int(n) for n, _ in entries]
        dates = [d for _, d in entries]
        last_date = max(dates)
        report["info"]["last_entry_date"] = last_date
        report["info"]["highest_entry_number"] = max(nums)
        if len(set(nums)) != len(nums):
            report["warnings"].append("Duplicate Entry numbers detected — entry numbers must be unique.")
        try:
            d = datetime.strptime(last_date, "%Y-%m-%d").date()
            report["info"]["days_since_last_entry"] = (date.today() - d).days
        except ValueError:
            pass

    report["info"]["backlog_open"] = len(OPEN_BACKLOG_RE.findall(log))
    report["info"]["backlog_resolved"] = len(DONE_BACKLOG_RE.findall(log))

    placeholders = len(re.findall(r"<[^>\n]{1,60}>", log))
    if placeholders:
        report["warnings"].append(
            f"{placeholders} unfilled '<placeholder>' token(s) remain in the log — "
            f"it looks freshly scaffolded and not yet filled in."
        )

    return report


# ---------------- paths ----------------

def _skill_dir():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _templates_dir():
    return os.path.join(_skill_dir(), "templates")


# ---------------- scaffold ----------------

def do_init(project_dir):
    """Create <project_dir>/.agent-eval/EVALUATION_LOG.md from the template (no overwrite)."""
    templates_dir = _templates_dir()
    src_path = os.path.join(templates_dir, "EVALUATION_LOG.template.md")
    if not os.path.isfile(src_path):
        print(f"ERROR: template not found: {src_path}", file=sys.stderr)
        return 1

    eval_dir = os.path.join(os.path.abspath(project_dir), EVAL_DIR)
    os.makedirs(eval_dir, exist_ok=True)
    dest = os.path.join(eval_dir, LOG_FILE)
    if os.path.exists(dest):
        print(f"Init target: {eval_dir}")
        print(f"  skipped (already present): {LOG_FILE}")
        return 0
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(read(src_path))

    print(f"Init target: {eval_dir}")
    print(f"  created: {LOG_FILE}")
    print(
        "\nNext: fill in the log's Purpose line (or just run `/agent-evaluation-layer` and let it seed\n"
        "it from your repo). The skill stages .agent-eval/ for you to review; you commit it yourself."
    )
    return 0


# ---------------- reporting ----------------

def print_report(report):
    line = "=" * 60
    print(line)
    print("Agent Evaluation Layer — Probe Report")
    print(line)
    print(f"project      : {report['project_dir']}")
    print(f"eval dir     : {report['eval_dir'] or '(none)'}")
    print(f"initialized  : {report['initialized']}")
    info = report.get("info", {})
    if info:
        print("-" * 60)
        for k in [
            "iteration_entries", "highest_entry_number", "last_entry_date",
            "days_since_last_entry", "backlog_open", "backlog_resolved",
        ]:
            if k in info:
                print(f"{k:24}: {info[k]}")
    if report["errors"]:
        print("-" * 60)
        print(f"ERRORS ({len(report['errors'])}):")
        for e in report["errors"]:
            print(f"  x {e}")
    if report["warnings"]:
        print("-" * 60)
        print(f"WARNINGS ({len(report['warnings'])}):")
        for w in report["warnings"]:
            print(f"  ! {w}")
    print(line)
    if report["errors"]:
        print("RESULT: NOT HEALTHY — fix the errors above.")
    elif report["warnings"]:
        print("RESULT: OK with warnings.")
    else:
        print("RESULT: HEALTHY")
    print(line)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scaffolder / health check for the Agent Evaluation Layer.")
    ap.add_argument("--dir", default=".", help="project directory (default: current dir)")
    ap.add_argument("--init", action="store_true", help="scaffold .agent-eval/EVALUATION_LOG.md only")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    ap.add_argument("--strict", action="store_true", help="treat warnings as a non-zero (2) exit")
    args = ap.parse_args(argv)

    did_action = False
    if args.init:
        rc = do_init(args.dir)
        if rc != 0:
            return rc
        did_action = True

    report = probe(args.dir)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    if report["errors"]:
        return 1
    if report["warnings"] and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
