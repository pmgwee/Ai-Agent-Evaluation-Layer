---
name: agent-evaluation-layer
description: >-
  Universal evaluation & iteration-refinement memory layer for any agent-built
  project, driven manually by the `/eval` command. Use it when the user wants to
  set up or update a project's durable memory of rules, rubrics, defects,
  lessons-learnt, and real feedback that survives across sessions and across
  different AI agents — for example "record this bug fix into the eval layer",
  "log this version's enhancement", "add this as a rule", or "set up the
  evaluation layer for this project". The user triggers it on demand; it does not
  run in the background. An OPTIONAL automatic mode (hooks + CLAUDE.md) exists for
  people who want it to run every iteration without asking.
disable-model-invocation: true
license: MIT
---

# Agent Evaluation Layer — Iteration Refinement

A drop-in memory-and-quality loop that lets any agent-built project **compound in
quality over time** instead of resetting each session. Enhancements, fixes, new
rules, rubrics, regulations, and real user feedback get captured into two durable
files that travel across sessions and across different AI agents.

This generalizes a proven pattern: a versioned **Spec** (the rules) plus an
append-only **Evaluation & Memory Log** (the memory of why each rule exists and
whether it's working).

> **This skill is manual by default.** It is marked `disable-model-invocation:
> true`, so it never runs on its own and never spends tokens in the background.
> It runs only when the user invokes the **`/eval`** command (or when an agent is
> explicitly told to follow it). An optional automatic mode is described at the
> end.

---

## Two ways to use it

**A) Manual — the `/eval` command (default, recommended).**
The user runs `/eval` at the moments they choose:
- **First run in a project** → bootstraps `.agent-eval/` (creates the Spec + Log).
- **Later runs** → records what the user names — `/eval fixed the rate-limit retry
  bug`, `/eval v2: added Stripe checkout`, `/eval add "never store secrets in
  logs" as a rule` — into the memory, then commits.

Nothing runs between invocations. This is the lowest-friction, lowest-token way
to use the layer.

**B) Automatic — hooks + CLAUDE.md (optional, advanced).**
For hands-off operation where the layer fires every iteration on its own. See
*Optional: automatic mode* below. Most users don't need this.

---

## What it creates

Everything lives inside the target project at **`.agent-eval/`**, committed to
the repo, so memory travels with the code:

```
<project-root>/
└── .agent-eval/
    ├── SPEC.md            # living rules, rubrics & regulations (versioned)
    └── EVALUATION_LOG.md  # append-only memory: feedback, defects, lessons, backlog
```

The Spec answers **"what are the rules right now?"** The Log answers **"why is
that a rule, what broke, what did we learn, what's next?"** Together they **are**
the system's persistent memory.

---

## The method (what `/eval` does each run)

### 1. Locate or bootstrap
- If `.agent-eval/` doesn't exist → **bootstrap** (see below), then continue.
- If it exists → read `SPEC.md` in full and the last 2–3 Iteration Log entries.

### 2. Record the iteration
Take what the user named for this run (a fix, an enhancement, a new
rule/rubric/regulation, or feedback). If they gave nothing, ask — or checkpoint
recent work using `git log`/`git diff` since the last entry. Then append a new
dated **Iteration Log** entry with: what changed, defects + root cause, lesson
learnt, user feedback near-verbatim, rubric result, and a suggested next
improvement.

### 3. Update rules if needed
If this run introduces a durable rule/rubric/regulation, add it to the Spec's
Rules and bump the Spec **Version History** *and* the Log's **Rules Changelog**
(keep them in sync — the probe checks this). Update the **Open Improvement
Backlog**: add new items, check off resolved ones and reference the entry.

### 4. Persist and report
Run the Spec's Self-Review Rubric against the recent work; log any misses as
defects. Commit the memory (`git add .agent-eval && git commit -m "eval: <summary>"`)
and report the entry number, any rule/version change, and the backlog delta.

> **Append-only.** Never rewrite or delete past Log entries — supersede with a new
> one and cross-reference it.

---

## Bootstrapping a new project

When `.agent-eval/` doesn't exist yet:

1. Create `.agent-eval/` and copy `templates/SPEC.template.md` →
   `.agent-eval/SPEC.md` and `templates/EVALUATION_LOG.template.md` →
   `.agent-eval/EVALUATION_LOG.md` (or run
   `python <skill>/scripts/probe.py --init --dir <project-root>`).
2. Seed the Spec from the repo: infer **Purpose** and **Source of Truth** from the
   README / package manifest / structure; propose 2–4 starter **Rules** and a
   short **Self-Review Rubric** fitting the stack. Ask the user at most 1–2 quick
   questions, and only if something critical is genuinely unclear.
3. Write **Iteration Log Entry 1 — <today> — Bootstrap**, then commit.

A thin, honest Spec beats a bloated, speculative one — the loop grows it.

---

## What counts as a "rule" worth versioning

Put something in the Spec (and log *why* in the Log) when it is a durable
constraint: a **rule** the user gave, a **rubric**/quality gate, a
**regulation**/policy (security, licensing, data-handling), or a **refinement**
that fixed a real defect and should never regress. One-off task details are not
rules — they live only in that iteration's Log entry.

---

## Searchability conventions

- Every Iteration Log entry is dated and numbered (`### Entry <N> — YYYY-MM-DD`);
  numbers are stable and never reused.
- Convert relative dates to absolute when writing ("yesterday" → the real date).
- Tag entries with a `Tags:` line (rule names, feature areas, defect types) and
  refer to recurring topics with a stable slug like `[[topic-name]]` so a plain
  text search lands on the right entry.

---

## Hard rules (anti-patterns)

- **Never rewrite or delete Log history** — append-only; supersede instead.
- **Never let the Spec and the Log's Rules Changelog drift** — a rule change
  updates both, in the same run.
- **Never invent results in the Log** — if the rubric wasn't fully run, say so.
- **Don't bloat the Spec with task trivia** — rules generalize; details go in the
  Log entry.

---

## Optional: automatic mode (hooks + CLAUDE.md)

Only if the user wants the layer to run every iteration **without** typing
`/eval`. This trades a small, constant token cost (a pointer loaded each session +
occasional reminders) for hands-off operation. Enable with:

```bash
python <skill>/scripts/probe.py --automate --dir <project-root>
```

It does two things:
- **`CLAUDE.md` pointer** — appended so every Claude Code session auto-loads the
  instruction to read/update `.agent-eval/`.
- **`SessionStart` + `Stop` hooks** (`hooks/agent_eval_hooks.py`) — SessionStart
  injects the layer's status; Stop nudges the agent to log an iteration when code
  changed but the Log didn't. The Stop nudge is loop-safe, never fires on
  read-only turns, and is silenced with the env var `AGENT_EVAL_ENFORCE=off`.

Turn it all back off (keeps `.agent-eval/` memory intact):

```bash
python <skill>/scripts/probe.py --disable --dir <project-root>
```

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

# Scaffold .agent-eval/ files only (usually /eval does this for you)
python scripts/probe.py --init --dir /path/to/project

# OPTIONAL automatic mode on / off
python scripts/probe.py --automate --dir /path/to/project
python scripts/probe.py --disable  --dir /path/to/project
```

The probe verifies both files exist, checks required sections, counts iteration
entries, reports the last entry date and open-backlog count, and flags Spec ↔
Changelog version drift. Exit `0` healthy, `1` missing structure, `2` warnings
under `--strict`.

---

## Files in this skill

- `commands/eval.md` — the `/eval` slash command (the manual trigger).
- `templates/SPEC.template.md` — starting point for a project's `SPEC.md`.
- `templates/EVALUATION_LOG.template.md` — starting point for `EVALUATION_LOG.md`.
- `templates/CLAUDE.snippet.md` — the CLAUDE.md pointer used by automatic mode.
- `reference/rubric.md` — a domain-agnostic rubric menu to build a project's rubric from.
- `scripts/probe.py` — installer (`--install-command`), scaffolder (`--init`),
  health check, and automatic-mode on/off (`--automate` / `--disable`).
- `hooks/agent_eval_hooks.py` + `hooks/settings.hooks.example.json` — the optional
  SessionStart/Stop hooks and reference config.
