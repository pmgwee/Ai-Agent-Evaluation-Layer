# Ai-Agent-Evaluation-Layer

**Language:** **English** · [中文](README.zh-CN.md)

A universal **Claude skill** that adds a durable, append-only *iteration history*
to any agent-built project — the record of **why** it changed: defects, root
causes, lessons, decisions, and real user feedback. You trigger it **manually**
with the **`/agent-evaluation-layer`** command whenever you want to record something, and it writes
that into one committed file that survives across sessions **and across different
AI agents**. It does **not** run in the background.

It maintains **one file** and is **not** a rules file: your project's own docs
(`CLAUDE.md`, README, ADRs) stay the source of truth for the *current* rules — so
there is never a second rules file to drift out of sync, and nothing this skill
does can affect your coding agent's behavior.

---

## How it works

You run `/agent-evaluation-layer` when you choose:

- **First run** → creates `.agent-eval/EVALUATION_LOG.md`.
- **Later runs** → e.g. `/agent-evaluation-layer fixed the rate-limit retry bug` → appends a dated entry and **stages** it (it never commits or pushes — you review and commit yourself).

Between runs: nothing happens, no tokens spent.

---

## What it does NOT touch (why it's safe to add anywhere)

- **No rules file.** It never creates a `SPEC.md` or any "current rules" file.
  Current rules stay in your project's own docs, so the two can't drift apart.
- **Never edits `CLAUDE.md`.** If a durable rule emerges, the log records a dated
  *pointer* and asks you to write the rule into your own docs — it never writes
  there itself.
- **No hooks, no session automation.** It injects nothing into sessions, blocks no
  turns, changes no agent behavior. `/agent-evaluation-layer` writes only
  `.agent-eval/EVALUATION_LOG.md`.

---

## Important: the log is read back manually

The layer injects nothing, so a **future session won't auto-read** the log. Make it
kick in one of two ways:

- **(a)** point an agent at it in the moment — *"check `.agent-eval/EVALUATION_LOG.md` first"*, or
- **(b)** add one line to **your own** `CLAUDE.md`, e.g. *"Before debugging, check `.agent-eval/EVALUATION_LOG.md` for past incidents."*

**(b)** is *you* writing in *your* doc (not the skill injecting anything) — it
keeps the zero-touch safety while making the log actually useful. **Recommended.**

---

## When to run `/agent-evaluation-layer`

**Judge by reusable lesson, not size.** Log it if it could recur elsewhere, has a
non-obvious root cause, or would bite a future agent again. A small fix can earn a
rule; a big ship can earn nothing. Pure one-off trivia (a typo) can stay in the
commit message.

**Run at checkpoints, not mid-flow.** Don't decide "is this worth logging?" every
fix — let changes accumulate, then run it once at a checkpoint (below). No
argument? It diffs `git log`/`git diff` since the last entry and surfaces what
changed.

**One entry per lesson, not per session.** Two unrelated defects = two entries
(easier to search later), not one merged blob.

**Good checkpoint triggers:**
- before switching sessions / handing off to another agent
- after a phase is implemented **and tested and confirmed done**
- right after any independent, reproducible lesson

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

Install = copy one folder into `.claude/skills/`. The skill runs by its **folder
name** (`/agent-evaluation-layer`), so there is **no command file and nothing goes
into `.claude/commands/`**. (Global `~/.claude/skills/` = all projects; project
`<project>/.claude/skills/` = one repo.)

**Option A — one prompt** (paste to your agent):

```
Help me install the agent-evaluation-layer skill:
https://raw.githubusercontent.com/pmgwee/Ai-Agent-Evaluation-Layer/main/docs/install.md
```

**Option B — manual:**

```bash
git clone https://github.com/pmgwee/Ai-Agent-Evaluation-Layer.git
cp -R Ai-Agent-Evaluation-Layer/skills/agent-evaluation-layer ~/.claude/skills/
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".\Ai-Agent-Evaluation-Layer\skills\agent-evaluation-layer" "$HOME\.claude\skills\"
```

Then type **`/agent-evaluation-layer`** in any project.

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
├── README.md · README.zh-CN.md   # docs (EN / CN)
├── LICENSE                        # MIT
├── docs/install.md                # agent-readable install manual
└── skills/agent-evaluation-layer/
    ├── SKILL.md                   # the method — invoked as /agent-evaluation-layer
    ├── templates/EVALUATION_LOG.template.md   # starting point for a project's log
    ├── reference/rubric.md        # optional eval-time review lens
    └── scripts/probe.py           # scaffolder + health check (installs nothing)
```

---

## License

MIT — see [LICENSE](LICENSE).
