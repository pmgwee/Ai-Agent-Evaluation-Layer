# Ai-Agent-Evaluation-Layer

**Language:** **English** · [中文](README.zh-CN.md)

A universal **Claude skill** that adds a self-improving *evaluation & iteration-
refinement memory* to any agent-built project. You trigger it **manually** with
the **`/eval`** command whenever you want to record something — a bug fix, a
version enhancement, a new rule — and it writes that into durable memory that
survives across sessions **and across different AI agents**. It does **not** run
in the background.

---

## How it works

You run `/eval` at the moments you choose:

- **First run in a project** → it sets up the layer (creates `.agent-eval/`).
- **Later runs** → `/eval fixed the rate-limit retry bug`, `/eval v2: added Stripe
  checkout`, `/eval add "never log secrets" as a rule` → it records that into
  memory and commits.

Between runs, nothing happens and no tokens are spent.

---

## When to run `/eval` — a practical guide

### 1. The Log records everything; the Spec only gets what's durable

Every `/eval` run appends an entry to `EVALUATION_LOG.md`. Whether that entry
*also* gets promoted into `SPEC.md`'s Rules section (with a version bump) comes
down to one test the agent applies each time: **is this durable** — will it
recur elsewhere, does it have a non-obvious root cause, would skipping it let
the same defect happen again? If yes, it becomes a versioned rule so future
iterations follow it automatically. If it's a one-off detail with no reusable
lesson, it stays in the Log entry only — the Spec doesn't need to grow for it.

This is a judgment call the agent makes each run by following the skill's
method, not a deterministic classifier — but the method is designed so you
don't have to pre-decide "is this rule-worthy?" yourself. A "small" fix can
absolutely earn a rule (e.g. a currency-formatting inconsistency traced to an
environment-dependent ICU bug is exactly the kind of small-diff, high-durability
lesson worth a rule); a "big" feature ship might add no rules at all if nothing
about it generalizes.

### 2. The checkpoint concept — defer the judgment, don't make it mid-flow

You don't need to stop and decide, the moment you fix something small, whether
it's "worth" logging. Let changes accumulate. At a natural checkpoint — before
switching sessions, or when a phase is genuinely implemented **and tested and
confirmed done** — run `/eval` once with no argument. It scans `git log` /
`git diff` since the last entry and surfaces everything that happened since;
the log-only-vs-rule-worthy judgment happens *then*, not while you're heads-down
coding.

### 3. One entry per lesson, not one entry per session

When a checkpoint sweeps up several independent, reproducible lessons, don't
compress them into a single entry. If you fixed two unrelated defects in the
same session and each teaches a distinct lesson, record **two** separate
Iteration Log entries (run `/eval` twice, or ask for two entries in one pass) —
not one entry that mixes both. A merged entry is much harder to find later by
date, keyword, or tag.

### 4. Good checkpoint triggers

- Before switching to a new session, or handing off to a different agent.
- After a phase is implemented **and tested and confirmed done** — not just
  "code written."
- Right after any independent, reproducible lesson — don't wait for the whole
  session to end before logging it; logging it immediately keeps entries small
  and searchable.

---

## What each project gets

```
<project>/.agent-eval/
├── SPEC.md            # living rules, rubrics & regulations (versioned)
└── EVALUATION_LOG.md  # append-only memory: feedback, defects, lessons, backlog
```

- **SPEC.md** — *"what are the rules right now?"* (versioned)
- **EVALUATION_LOG.md** — *"why is that a rule, what broke, what did we learn,
  what's next?"* (append-only, searchable)

Committed to the repo, so `git pull` restores full context on any machine, in any
session, for any agent.

---

## Install

### Option A (recommended) — one prompt

Paste this to your agent (Claude Code, Cursor, etc.):

```
Help me install the agent-evaluation-layer skill:
https://raw.githubusercontent.com/pmgwee/Ai-Agent-Evaluation-Layer/main/docs/install.md
```

`docs/install.md` is written for the agent to read: it copies the skill into
`.claude/skills/`, installs the `/eval` command, and tells you how to use it.

### Option B — manual

```bash
git clone https://github.com/pmgwee/Ai-Agent-Evaluation-Layer.git
# 1) copy the skill (global = all projects on this machine)
cp -R Ai-Agent-Evaluation-Layer/skills/agent-evaluation-layer ~/.claude/skills/
# 2) install the /eval command (global)
python3 ~/.claude/skills/agent-evaluation-layer/scripts/probe.py --install-command
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".\Ai-Agent-Evaluation-Layer\skills\agent-evaluation-layer" "$HOME\.claude\skills\"
python "$HOME\.claude\skills\agent-evaluation-layer\scripts\probe.py" --install-command
```

Then, in any project, just type **`/eval`**. That's it.

---

## Optional: automatic mode

If you'd rather the layer run on **every** iteration without typing `/eval`, turn
on automatic mode (adds a `CLAUDE.md` pointer + `SessionStart`/`Stop` hooks). This
costs a little extra token overhead per session.

```bash
python3 <skill>/scripts/probe.py --automate --dir /path/to/project   # turn on
python3 <skill>/scripts/probe.py --disable  --dir /path/to/project   # turn off
```

The Stop reminder can also be silenced anytime with `AGENT_EVAL_ENFORCE=off`.

---

## Health check

```bash
python3 <skill>/scripts/probe.py --dir /path/to/project           # human report
python3 <skill>/scripts/probe.py --dir /path/to/project --json    # machine-readable
python3 <skill>/scripts/probe.py --dir /path/to/project --strict  # warnings -> exit 2
```

No `pip install` needed.

---

## Repository layout

```
Ai-Agent-Evaluation-Layer/
├── README.md                                # this file (English)
├── README.zh-CN.md                          # Chinese translation
├── LICENSE
├── docs/
│   └── install.md                           # agent-readable install manual (bilingual)
└── skills/
    └── agent-evaluation-layer/
        ├── SKILL.md                          # the method (manual by default)
        ├── commands/
        │   └── eval.md                       # the /eval slash command (manual trigger)
        ├── templates/
        │   ├── SPEC.template.md
        │   ├── EVALUATION_LOG.template.md
        │   └── CLAUDE.snippet.md             # pointer used by optional automatic mode
        ├── reference/
        │   └── rubric.md                     # rubric menu
        ├── hooks/                            # optional automatic mode
        │   ├── agent_eval_hooks.py
        │   └── settings.hooks.example.json
        └── scripts/
            └── probe.py                      # installer / health check / automate / disable
```

---

## License

MIT — see [LICENSE](LICENSE).
