# Ai-Agent-Evaluation-Layer

**Language:** **English** · [中文](README.zh-CN.md)

A universal **Claude skill** that adds a durable, append-only *iteration history*
to any agent-built project — the record of **why** it changed: defects, root
causes, lessons, decisions, and real user feedback. You trigger it **manually**
with the **`/eval`** command whenever you want to record something, and it writes
that into one committed file that survives across sessions **and across different
AI agents**. It does **not** run in the background.

It maintains **one file** and is **not** a rules file: your project's own docs
(`CLAUDE.md`, README, ADRs) stay the source of truth for the *current* rules — so
there is never a second rules file to drift out of sync, and nothing this skill
does can affect your coding agent's behavior.

---

## How it works

You run `/eval` at the moments you choose:

- **First run in a project** → it sets up the layer (creates
  `.agent-eval/EVALUATION_LOG.md`).
- **Later runs** → `/eval fixed the rate-limit retry bug`, `/eval v2: added Stripe
  checkout` → it appends a dated entry and commits.

Between runs, nothing happens and no tokens are spent.

---

## What it does NOT touch (why it's safe to add anywhere)

- **No rules file.** It never creates a `SPEC.md` or any "current rules" file.
  Current rules stay in your project's own docs, so the two can't drift apart.
- **Never edits `CLAUDE.md`.** If a durable rule emerges, the log records a dated
  *pointer* and asks you to write the rule into your own docs — it never writes
  there itself.
- **No hooks, no session automation.** It injects nothing into sessions, blocks no
  turns, changes no agent behavior. `/eval` writes only
  `.agent-eval/EVALUATION_LOG.md`.

---

## Important: the log is read back manually, too

Because this layer injects nothing into sessions, the log **does not automatically
feed future agents**. A later Claude Code session won't know the log exists or read
it on its own — unless you either:

- **(a)** tell it in the moment — *"check `.agent-eval/EVALUATION_LOG.md` first"*, or
- **(b)** add one line to your **own** `CLAUDE.md`, e.g. *"Before debugging, check
  `.agent-eval/EVALUATION_LOG.md` for related past incidents."*

Option **(b)** is *you* writing into *your own* rules doc — not the skill injecting
anything — so it keeps the zero-touch safety while making the "future agents don't
repeat past mistakes" value actually kick in. **Recommended.** Without one of these,
the log only helps when you manually look back or manually point an agent at it.

---

## When to run `/eval` — a practical guide

### 1. Log everything meaningful; keep current rules in your own docs

Every `/eval` run appends an entry to `EVALUATION_LOG.md`. Whether a lesson *also*
earns a durable **rule** comes down to one test the agent applies each time: **is
this durable** — will it recur elsewhere, does it have a non-obvious root cause,
would skipping it let the same defect happen again? If yes, you record the rule in
your project's own docs (e.g. `CLAUDE.md`) and the log keeps a dated pointer to it.
If it's a one-off detail with no reusable lesson, it stays in the Log entry only.

This is a judgment the agent makes each run by following the skill's method, not a
deterministic classifier — but the method is designed so you don't have to
pre-decide "is this rule-worthy?" yourself. A "small" fix can absolutely earn a
rule (e.g. a currency-formatting inconsistency traced to an environment-dependent
ICU bug is exactly the kind of small-diff, high-durability lesson worth a rule); a
"big" feature ship might add nothing if nothing about it generalizes.

### 2. The checkpoint concept — defer the judgment, don't make it mid-flow

You don't need to stop and decide, the moment you fix something small, whether
it's "worth" logging. Let changes accumulate. At a natural checkpoint — before
switching sessions, or when a phase is genuinely implemented **and tested and
confirmed done** — run `/eval` once with no argument. It scans `git log` /
`git diff` since the last entry and surfaces everything that happened since; the
what-to-log judgment happens *then*, not while you're heads-down coding.

### 3. One entry per lesson, not one entry per session

When a checkpoint sweeps up several independent, reproducible lessons, don't
compress them into a single entry. If you fixed two unrelated defects in the same
session and each teaches a distinct lesson, record **two** separate Iteration Log
entries (run `/eval` twice, or ask for two entries in one pass) — not one entry
that mixes both. A merged entry is much harder to find later by date, keyword, or
tag.

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
└── EVALUATION_LOG.md  # append-only history: why things changed — feedback,
                       # defects, root causes, lessons, decisions, backlog
```

One file, committed to the repo, so `git pull` restores full history on any
machine, in any session, for any agent. It records the dated *history* your
snapshot docs (`CLAUDE.md`, README, ADRs) don't keep — it never restates the
current rules those docs already hold.

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
        ├── SKILL.md                          # the method (manual; one file, no rules file, no hooks)
        ├── commands/
        │   └── eval.md                       # the /eval slash command (manual trigger)
        ├── templates/
        │   └── EVALUATION_LOG.template.md    # starting point for a project's log
        ├── reference/
        │   └── rubric.md                     # optional eval-time review lens
        └── scripts/
            └── probe.py                      # installer / scaffolder / health check
```

---

## License

MIT — see [LICENSE](LICENSE).
