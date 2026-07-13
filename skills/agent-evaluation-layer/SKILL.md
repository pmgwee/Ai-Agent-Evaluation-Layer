---
name: agent-evaluation-layer
description: >-
  Universal, append-only iteration-history memory for any agent-built project,
  driven manually by the `/eval` command. Use it when the user wants to record
  WHY the project changed — a bug fix's root cause, a version's lesson, a decision
  and its rationale, or real user feedback — into a durable, dated log that
  survives across sessions and across different AI agents. For example "record
  this bug fix into the eval log", "log this version's enhancement", or "set up
  the evaluation log for this project". It maintains ONE file
  (`.agent-eval/EVALUATION_LOG.md`); it is NOT a rules file and never edits the
  project's own docs. The user triggers it on demand; it never runs in the
  background.
disable-model-invocation: true
license: MIT
---

# Agent Evaluation Layer — Iteration History

A drop-in memory loop that lets any agent-built project **remember why it changed**
instead of resetting each session. Defects, root causes, lessons, decisions, and
real user feedback get captured into one durable, dated file that travels across
sessions and across different AI agents.

The layer maintains exactly one artifact: an append-only **Evaluation & Memory
Log**. It answers **"what broke, why, what did we learn, what's next?"** — the
dated history that a project's snapshot docs (README, `CLAUDE.md`, ADRs)
deliberately don't keep.

> **This skill is manual.** It is marked `disable-model-invocation: true`, so it
> never runs on its own and never spends tokens in the background. It runs only
> when the user invokes the **`/eval`** command (or when an agent is explicitly
> told to follow it).

---

## What it deliberately does NOT do

This layer is designed to add memory **without** interfering with the host agent
or the project's own configuration. By design it:

- **Does not keep a "current rules" file.** There is no `SPEC.md`. The project's
  own docs (`CLAUDE.md`, README, ADRs) stay the single source of truth for current
  rules — so there is never a second rules file to drift out of sync with them.
- **Does not edit `CLAUDE.md`** or any project rules doc. If a durable rule
  emerges, the layer records a dated *pointer* in its log and asks the user to
  write the rule into their own docs — it never writes there itself.
- **Does not install hooks, settings, or session automation.** It injects nothing
  into sessions, blocks no turns, and changes no agent behavior. Running `/eval`
  writes only `.agent-eval/EVALUATION_LOG.md`.

This is what keeps the layer safe to add to any repo — including one already
governed by a `CLAUDE.md` — with zero risk to the coding agent's behavior or
answer quality.

---

## What it creates

Everything lives inside the target project at **`.agent-eval/`**, committed to the
repo, so memory travels with the code:

```
<project-root>/
└── .agent-eval/
    └── EVALUATION_LOG.md   # append-only memory: history, feedback, defects, decisions, backlog
```

Its sections: **Decisions & Rules History** (a dated index pointing to where each
current rule actually lives), **Open Improvement Backlog**, and the **Iteration
Log** (dated, numbered entries).

---

## The method (what `/eval` does each run)

### 1. Locate or bootstrap
- If `.agent-eval/EVALUATION_LOG.md` doesn't exist → **bootstrap** (see below),
  then continue.
- If it exists → read its Open Improvement Backlog and the last 2–3 Iteration Log
  entries.

### 2. Record the iteration
Take what the user named for this run (a fix, an enhancement, a decision, or
feedback). If they gave nothing, ask — or checkpoint recent work using `git
log`/`git diff` since the last entry. Then append a new dated **Iteration Log**
entry with: what changed, defects + root cause, lesson learnt, user feedback
near-verbatim, optional self-review notes, and a suggested next improvement.
Record **one entry per independent, reproducible lesson**, not one merged entry
per session.

### 3. Record durable decisions as pointers (not as rules)
If this run produced a durable rule/decision, add a dated one-line pointer under
**Decisions & Rules History** (what was adopted, why, and where the rule now
lives), and tell the user to write the actual rule into their own project docs
(e.g. `CLAUDE.md`). Never create a rules file and never edit `CLAUDE.md` yourself
unless the user explicitly asks. Update the **Open Improvement Backlog**: add new
items, check off resolved ones and reference the entry.

### 4. Persist and report
Optionally apply the reference rubric (`reference/rubric.md`) as a lens to find
issues worth logging. Commit the memory (`git add .agent-eval && git commit -m
"eval: <summary>"`) and report the entry number, any decision pointer (plus the
reminder to update the project's own docs), and the backlog delta.

> **Append-only.** Never rewrite or delete past Log entries — supersede with a new
> one and cross-reference it.

---

## Bootstrapping a new project

When `.agent-eval/EVALUATION_LOG.md` doesn't exist yet:

1. Create `.agent-eval/` and copy `templates/EVALUATION_LOG.template.md` →
   `.agent-eval/EVALUATION_LOG.md` (or run
   `python <skill>/scripts/probe.py --init --dir <project-root>`).
2. Fill the log's **Purpose** line from the repo (infer what the project is from
   the README / package manifest / structure). Do **not** copy in a set of rules —
   the project's own docs already hold those.
3. Write **Iteration Log Entry 1 — <today> — Bootstrap**, then commit.

---

## What is worth logging

Log something when it has **durability** — it will recur elsewhere, has a
non-obvious root cause, or a future agent would re-hit the same problem without
this record. A small fix can absolutely be worth an entry (a currency-formatting
bug traced to environment-dependent behavior is small-diff but high-durability); a
big feature ship might add nothing if nothing about it generalizes. Judge by
reusable lesson, not by diff size. Pure one-off task trivia (a typo, a style
tweak with no root cause) can stay in the commit message and skip the log.

---

## Searchability conventions

- Every Iteration Log entry is dated and numbered (`### Entry <N> — YYYY-MM-DD`);
  numbers are stable and never reused.
- Convert relative dates to absolute when writing ("yesterday" → the real date).
- Tag entries with a `Tags:` line and refer to recurring topics with a stable slug
  like `[[topic-name]]` so a plain text search lands on the right entry.

---

## Hard rules (anti-patterns)

- **Never rewrite or delete Log history** — append-only; supersede instead.
- **Never create a `SPEC.md` / rules file, and never edit `CLAUDE.md`** — record a
  pointer and let the user own their rules docs.
- **Never install hooks or session automation** from this skill.
- **Never invent results in the Log** — if you didn't verify something, say so.
- **Don't restate current rules in the Log** — rules generalize and live in the
  project's own docs; the Log records the dated *history* of why they exist.

---

## CLI (`scripts/probe.py`)

Dependency-free (Python 3 standard library only).

```bash
# PRIMARY: install the /eval command (once; global = every project on this machine)
python scripts/probe.py --install-command                       # global
python scripts/probe.py --install-command --scope project --dir /path/to/project

# Health report on a project's layer
python scripts/probe.py --dir /path/to/project
python scripts/probe.py --dir /path/to/project --json           # machine-readable
python scripts/probe.py --dir /path/to/project --strict         # warnings -> exit 2

# Scaffold .agent-eval/EVALUATION_LOG.md only (usually /eval does this for you)
python scripts/probe.py --init --dir /path/to/project
```

The probe verifies the log exists, checks its required sections, counts iteration
entries, and reports the last entry date and open-backlog count. Exit `0` healthy,
`1` missing structure, `2` warnings under `--strict`.

---

## Files in this skill

- `commands/eval.md` — the `/eval` slash command (the manual trigger).
- `templates/EVALUATION_LOG.template.md` — starting point for a project's `EVALUATION_LOG.md`.
- `reference/rubric.md` — a domain-agnostic rubric menu, used as an optional eval-time lens.
- `scripts/probe.py` — installer (`--install-command`), scaffolder (`--init`), and health check.
