#!/usr/bin/env python3
"""
probe.py — health check, scaffolder & installer for the Agent Evaluation Layer.

Dependency-free (Python 3 standard library only).

Primary (manual) model:
    python probe.py --install-command                 # install the /eval command (global)
    python probe.py --install-command --scope project --dir /path/to/project
    #   then, in Claude Code, just type `/eval` — first run bootstraps the
    #   project's .agent-eval/, later runs record a fix/enhancement/rule.

Other modes:
    python probe.py --dir /path/to/project            # health report
    python probe.py --init --dir /path/to/project     # scaffold .agent-eval/ files only
    python probe.py --automate --dir /path/to/project # OPTIONAL: add CLAUDE.md pointer + hooks
    python probe.py --disable --dir /path/to/project  # remove CLAUDE.md pointer + hooks
    python probe.py --dir /path/to/project --json      # machine-readable report
    python probe.py --dir /path/to/project --strict    # warnings -> non-zero exit

Exit codes:
    0  healthy / action ok
    1  not initialized, or missing required files/sections (hard failure)
    2  healthy structure but warnings present, and --strict was set
"""

import argparse
import json
import os
import re
import sys
from datetime import date, datetime

EVAL_DIR = ".agent-eval"
SPEC_FILE = "SPEC.md"
LOG_FILE = "EVALUATION_LOG.md"
CLAUDE_SNIPPET_MARKER = "<!-- agent-evaluation-layer:start -->"
CLAUDE_SNIPPET_END = "<!-- agent-evaluation-layer:end -->"

SPEC_REQUIRED = [
    ("Purpose", r"^#+\s*.*purpose"),
    ("Source of Truth", r"^#+\s*.*source of truth"),
    ("Rules", r"^#+\s*.*rules"),
    ("Self-Review Rubric", r"^#+\s*.*self[- ]?review rubric"),
    ("Version History", r"^#+\s*.*version history"),
]
LOG_REQUIRED = [
    ("How to use", r"^#+\s*.*how .*use this file"),
    ("Rules Changelog", r"^#+\s*.*rules changelog"),
    ("Open Improvement Backlog", r"^#+\s*.*open improvement backlog"),
    ("Iteration Log", r"^#+\s*.*iteration log"),
]

ENTRY_RE = re.compile(r"^###\s+Entry\s+(\d+)\s+—\s+(\d{4}-\d{2}-\d{2})", re.M | re.I)
ENTRY_RE_LOOSE = re.compile(r"^###\s+Entry\s+(\d+)\b", re.M | re.I)
OPEN_BACKLOG_RE = re.compile(r"^\s*[-*]\s*\[\s*\]\s+", re.M)
DONE_BACKLOG_RE = re.compile(r"^\s*[-*]\s*\[[xX]\]\s+", re.M)
SPEC_VERSION_ROW_RE = re.compile(r"^\|\s*([0-9][^|]*?)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|", re.M)


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
            f"Run `/eval` in Claude Code (or `probe.py --init`) to create one."
        )
        return report

    report["project_dir"] = root
    eval_dir = os.path.join(root, EVAL_DIR)
    report["eval_dir"] = eval_dir
    report["initialized"] = True

    spec_path = os.path.join(eval_dir, SPEC_FILE)
    log_path = os.path.join(eval_dir, LOG_FILE)

    if not os.path.isfile(spec_path):
        report["errors"].append(f"Missing {EVAL_DIR}/{SPEC_FILE}")
    if not os.path.isfile(log_path):
        report["errors"].append(f"Missing {EVAL_DIR}/{LOG_FILE}")
    if report["errors"]:
        return report

    spec = read(spec_path)
    log = read(log_path)

    _, spec_missing = check_sections(spec, SPEC_REQUIRED)
    _, log_missing = check_sections(log, LOG_REQUIRED)
    for m in spec_missing:
        report["errors"].append(f"{SPEC_FILE} is missing required section: {m}")
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

    version_rows = SPEC_VERSION_ROW_RE.findall(spec)
    if version_rows:
        latest_version = version_rows[-1][0].strip()
        latest_v_date = version_rows[-1][1].strip()
        report["info"]["spec_latest_version"] = latest_version
        report["info"]["spec_latest_version_date"] = latest_v_date
        changelog_idx = re.search(r"rules changelog", log, re.I)
        changelog_text = log[changelog_idx.start():] if changelog_idx else log
        if latest_v_date not in changelog_text:
            report["warnings"].append(
                f"Spec's latest version ({latest_version}, {latest_v_date}) is not referenced "
                f"in the Log's Rules Changelog — Spec and Changelog may have drifted."
            )
    else:
        report["warnings"].append(f"No Version History rows parsed in {SPEC_FILE}.")

    placeholders = len(re.findall(r"<[^>\n]{1,60}>", spec)) + len(re.findall(r"<[^>\n]{1,60}>", log))
    if placeholders:
        report["warnings"].append(
            f"{placeholders} unfilled '<placeholder>' token(s) remain in the Spec/Log — "
            f"the layer looks freshly scaffolded and not yet filled in."
        )

    return report


# ---------------- paths ----------------

def _skill_dir():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _templates_dir():
    return os.path.join(_skill_dir(), "templates")


def _commands_target(project_dir, scope):
    if scope == "global":
        return os.path.join(os.path.expanduser("~"), ".claude", "commands")
    return os.path.join(os.path.abspath(project_dir), ".claude", "commands")


# ---------------- primary: manual command install ----------------

def install_command(project_dir, scope="global"):
    """Install the /eval slash command (global by default, or project-scoped)."""
    src = os.path.join(_skill_dir(), "commands", "eval.md")
    if not os.path.isfile(src):
        print(f"ERROR: command template not found: {src}", file=sys.stderr)
        return 1
    dest_dir = _commands_target(project_dir, scope)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "eval.md")
    existed = os.path.isfile(dest)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(read(src))
    print(f"  command: {'updated' if existed else 'installed'} /eval -> {dest}  (scope: {scope})")
    print("  usage: type `/eval` in Claude Code — first run bootstraps this project's")
    print("         .agent-eval/; later runs: `/eval <what to record>`.")
    return 0


# ---------------- scaffold ----------------

def do_init(project_dir):
    """Create <project_dir>/.agent-eval/ memory files from templates (no overwrite). Files only."""
    templates_dir = _templates_dir()
    src = {
        SPEC_FILE: os.path.join(templates_dir, "SPEC.template.md"),
        LOG_FILE: os.path.join(templates_dir, "EVALUATION_LOG.template.md"),
    }
    for label, path in src.items():
        if not os.path.isfile(path):
            print(f"ERROR: template not found: {path}", file=sys.stderr)
            return 1

    eval_dir = os.path.join(os.path.abspath(project_dir), EVAL_DIR)
    os.makedirs(eval_dir, exist_ok=True)
    created, skipped = [], []
    for dest_name, path in src.items():
        dest = os.path.join(eval_dir, dest_name)
        if os.path.exists(dest):
            skipped.append(dest_name)
            continue
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(read(path))
        created.append(dest_name)

    print(f"Init target: {eval_dir}")
    if created:
        print("  created: " + ", ".join(created))
    if skipped:
        print("  skipped (already present): " + ", ".join(skipped))
    print(
        "\nNext: fill in the Spec (or just run `/eval` and let it seed the Spec from\n"
        "your repo), then commit .agent-eval/."
    )
    return 0


# ---------------- OPTIONAL: automatic mode (CLAUDE.md pointer + hooks) ----------------

def append_claude_md(project_dir):
    snippet_path = os.path.join(_templates_dir(), "CLAUDE.snippet.md")
    if not os.path.isfile(snippet_path):
        print(f"  CLAUDE.md: snippet template not found ({snippet_path}) — skipped", file=sys.stderr)
        return
    snippet = read(snippet_path).strip()
    claude_path = os.path.join(os.path.abspath(project_dir), "CLAUDE.md")
    existing = read(claude_path) if os.path.isfile(claude_path) else ""
    if CLAUDE_SNIPPET_MARKER in existing:
        print("  CLAUDE.md: pointer already present — skipped")
        return
    if existing == "" or existing.endswith("\n\n"):
        sep = ""
    elif existing.endswith("\n"):
        sep = "\n"
    else:
        sep = "\n\n"
    with open(claude_path, "a", encoding="utf-8") as fh:
        fh.write(sep + snippet + "\n")
    print(f"  CLAUDE.md: {'created' if not existing else 'appended pointer to'} {claude_path}")


def install_hooks(project_dir):
    hook_script = os.path.join(_skill_dir(), "hooks", "agent_eval_hooks.py")
    if not os.path.isfile(hook_script):
        print(f"ERROR: hook script not found: {hook_script}", file=sys.stderr)
        return 1
    python = sys.executable or "python3"
    settings_dir = os.path.join(os.path.abspath(project_dir), ".claude")
    os.makedirs(settings_dir, exist_ok=True)
    settings_path = os.path.join(settings_dir, "settings.json")

    settings = {}
    if os.path.isfile(settings_path):
        try:
            settings = json.loads(read(settings_path))
        except Exception as e:
            print(f"ERROR: could not parse {settings_path}: {e}", file=sys.stderr)
            return 1
    hooks = settings.setdefault("hooks", {})

    events = {"SessionStart": "session-start", "Stop": "stop"}
    changed = False
    for event, mode in events.items():
        groups = hooks.setdefault(event, [])
        already = any(
            any(
                h.get("type") == "command"
                and isinstance(h.get("args"), list)
                and hook_script in h.get("args", [])
                and mode in h.get("args", [])
                for h in g.get("hooks", [])
            )
            for g in groups if isinstance(g, dict)
        )
        if already:
            continue
        groups.append({
            "hooks": [{
                "type": "command",
                "command": python,
                "args": [hook_script, "--event", mode],
            }]
        })
        changed = True

    if changed:
        with open(settings_path, "w", encoding="utf-8") as fh:
            json.dump(settings, fh, indent=2)
            fh.write("\n")
        print(f"  hooks: installed SessionStart + Stop -> {settings_path}")
        print(f"         interpreter: {python}")
        print(f"         handler    : {hook_script}")
    else:
        print(f"  hooks: already installed in {settings_path} — skipped")
    return 0


def automate(project_dir):
    print("Enabling OPTIONAL automatic mode (CLAUDE.md pointer + hooks):")
    append_claude_md(project_dir)
    return install_hooks(project_dir)


def disable_automation(project_dir):
    """Remove the CLAUDE.md pointer block and the layer's hooks. Leaves .agent-eval/ intact."""
    root = os.path.abspath(project_dir)
    changed = False

    claude_path = os.path.join(root, "CLAUDE.md")
    if os.path.isfile(claude_path):
        text = read(claude_path)
        if CLAUDE_SNIPPET_MARKER in text and CLAUDE_SNIPPET_END in text:
            i = text.index(CLAUDE_SNIPPET_MARKER)
            j = text.index(CLAUDE_SNIPPET_END) + len(CLAUDE_SNIPPET_END)
            new = text[:i] + text[j:]
            new = re.sub(r"\n{3,}", "\n\n", new).strip()
            new = (new + "\n") if new else ""
            with open(claude_path, "w", encoding="utf-8") as fh:
                fh.write(new)
            print("  CLAUDE.md: removed evaluation-layer pointer")
            changed = True

    settings_path = os.path.join(root, ".claude", "settings.json")
    if os.path.isfile(settings_path):
        try:
            settings = json.loads(read(settings_path))
        except Exception as e:
            print(f"ERROR: could not parse {settings_path}: {e}", file=sys.stderr)
            settings = None
        if isinstance(settings, dict) and isinstance(settings.get("hooks"), dict):
            removed = False
            for event in ("SessionStart", "Stop"):
                groups = settings["hooks"].get(event)
                if not isinstance(groups, list):
                    continue
                kept = []
                for g in groups:
                    hs = g.get("hooks", []) if isinstance(g, dict) else []
                    refs = any(
                        isinstance(arg, str) and "agent_eval_hooks.py" in arg
                        for h in hs for arg in h.get("args", [])
                    )
                    if refs:
                        removed = True
                    else:
                        kept.append(g)
                if kept:
                    settings["hooks"][event] = kept
                else:
                    settings["hooks"].pop(event, None)
            if not settings["hooks"]:
                settings.pop("hooks", None)
            if removed:
                with open(settings_path, "w", encoding="utf-8") as fh:
                    json.dump(settings, fh, indent=2)
                    fh.write("\n")
                print(f"  hooks: removed evaluation-layer hooks from {settings_path}")
                changed = True

    if not changed:
        print("  nothing to disable (no CLAUDE.md pointer or hooks found).")
    print("  note: .agent-eval/ memory files are left in place (they cost nothing unless read).")
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
            "spec_latest_version", "spec_latest_version_date",
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
    ap = argparse.ArgumentParser(description="Health check / installer for the Agent Evaluation Layer.")
    ap.add_argument("--dir", default=".", help="project directory (default: current dir)")
    ap.add_argument("--install-command", action="store_true", help="install the /eval slash command (primary, manual model)")
    ap.add_argument("--scope", choices=["global", "project"], default="global", help="where to install /eval (default: global)")
    ap.add_argument("--init", action="store_true", help="scaffold .agent-eval/ memory files only (no CLAUDE.md, no hooks)")
    ap.add_argument("--automate", action="store_true", help="OPTIONAL: enable automatic mode (CLAUDE.md pointer + SessionStart/Stop hooks)")
    ap.add_argument("--disable", action="store_true", help="remove the CLAUDE.md pointer + hooks (leaves .agent-eval/ intact)")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    ap.add_argument("--strict", action="store_true", help="treat warnings as a non-zero (2) exit")
    args = ap.parse_args(argv)

    if args.disable:
        return disable_automation(args.dir)

    did_action = False
    if args.install_command:
        rc = install_command(args.dir, args.scope)
        if rc != 0:
            return rc
        did_action = True
    if args.init:
        rc = do_init(args.dir)
        if rc != 0:
            return rc
        did_action = True
    if args.automate:
        rc = automate(args.dir)
        if rc != 0:
            return rc
        did_action = True

    # Report (always, unless we only installed the global command with no local layer).
    report = probe(args.dir)
    if args.json:
        print(json.dumps(report, indent=2))
    elif not (did_action and not report["initialized"]):
        print_report(report)

    if report["errors"] and did_action and not report["initialized"]:
        # Installing the global command without a local layer is fine — not an error state.
        return 0
    if report["errors"]:
        return 1
    if report["warnings"] and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
