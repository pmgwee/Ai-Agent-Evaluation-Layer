---
name: agent-evaluation-layer
description: >-
  Universal evaluation & iteration-refinement layer for any agent-built software
  project. Use this skill whenever the user wants their project or agent to
  self-improve across iterations, keep memory across sessions and across
  different AI agents, track defects / weaknesses / lessons-learnt, maintain a
  versioned spec of rules, rubrics and regulations, capture real user feedback
  into durable searchable memory, run a self-review or quality-gate rubric
  before shipping, or push a system toward production-grade / top-tier quality.
  Trigger it at the START of a work session on such a project (to load prior
  context) and BEFORE ENDING a turn (to record what changed) — even if the user
  never says the words "evaluation layer". Also use when setting up this loop for
  a new project, or when asked to review a system for possible defects and next
  improvements.
license: MIT
---

# Agent Evaluation Layer — Iteration Refinement

A drop-in memory-and-quality loop that makes any agent-built project **compound
in quality every iteration** instead of resetting each session. It gives a
project two durable files and one repeatable loop, so that enhancements, fixes,
new rules, rubrics, regulations, and real user feedback are captured the moment
they happen and carried forward across sessions and across different AI agents.

This is a generalization of a proven pattern: a versioned **Spec** (the rules)
plus an append-only **Evaluation & Memory Log** (the memory of why each rule
exists and whether it's working). This skill turns that pattern into something
you can drop into *every* repo.

---

## What this skill creates

Everything lives inside the target project at **`.agent-eval/`** and is
committed to the repo, so the memory travels with the code — any future session,
any agent, on any machine, starts with full context after a `git pull`.

```
<project-root>/
└── .agent-eval/
    ├── SPEC.md            # living rules, rubrics & regulations (versioned)
    └── EVALUATION_LOG.md  # append-only memory: feedback, defects, lessons, backlog
```

Two files, on purpose. The Spec answers **"what are the rules right now?"** The
Log answers **"why is that a rule, what broke, what did we learn, what's next?"**
Together they *are* the system's persistent memory.

---

## The core loop (run this every iteration)

Follow these seven steps on every task against a project that uses this layer.
Steps 1 and 6–7 are non-negotiable — they are what makes memory survive.

### 1. Load context (session start / new task)
- If `.agent-eval/` does **not** exist → this is a new project. Go to
  **Bootstrapping** below, then continue.
- If it exists:
  - Read `.agent-eval/SPEC.md` **in full**.
  - Read the Log's **Rules Changelog**, **Open Improvement Backlog**, and the
    **last 2–3 Iteration Log entries**. (Older entries stay searchable but you
    don't need them all in context.)
  - Optionally run the probe for a fast health check:
    `python <skill>/scripts/probe.py --dir <project-root>`
    (path depends on where the skill is installed; see **Probe** below).

### 2. Do the work — strictly per the current Spec
Every current rule in the Spec applies. Do not silently deviate. If the user's
new request *conflicts* with a Spec rule, surface the conflict rather than
quietly overriding it — then, if they confirm the change, treat it as a rule
change (step 6).

### 3. Self-review against the rubric
Run the **Self-Review Rubric** from the Spec against what you just produced.
Check each item **by name/number**. Every failing item is a **Defect** — record
it in this iteration's entry with a one-line root cause, don't just fix it
silently. (A defect that's caught and fixed is still a logged lesson.)

### 4. Capture the brief and the feedback — near-verbatim
Record the user's request for this iteration, and any feedback they gave
(positive **or** corrective), close to word-for-word. Don't paraphrase away the
specifics — a future agent needs the exact ask, not your summary of it.
Confirmations matter as much as corrections: if the user validated a non-obvious
choice, log it so the system doesn't drift away from something that already
worked.

### 5. Advisory pass — the system reviews itself
This is the step that drives the project toward production-grade. Independently
of the immediate task, inspect the **current system** for latent problems and
propose concrete next improvements:
- What defect, weakness, edge case, scaling limit, security gap, or maintenance
  burden is *likely to bite next*, even if nothing broke this time?
- What would move this closer to top-tier / production-scale quality?

Write each finding into the **Open Improvement Backlog** as an actionable item.
Advise — don't auto-implement — unless the user asks.

### 6. Write memory (append, never overwrite)
Append a new dated entry to the **Iteration Log** using the entry template in
`EVALUATION_LOG.template.md`. Then:
- If any **rule, rubric, or regulation changed**, update the Log's **Rules
  Changelog** *and* bump the **Version History** table in the Spec (keep them in
  sync — the probe checks this).
- Move any backlog items you resolved out of the backlog and reference them from
  the entry (check them off — never delete history).

### 7. Persist
- **In a git project (Claude Code / normal repo):** stage and commit the
  `.agent-eval/` changes so they travel across sessions and agents, e.g.
  `git add .agent-eval && git commit -m "eval: iteration <N> — <short summary>"`.
  Commit the memory update *with* the work it describes when practical.
- **In Cowork (no automatic cross-session memory):** surface the updated
  `.agent-eval/SPEC.md` and `.agent-eval/EVALUATION_LOG.md` back to the user and
  remind them these two files (plus any source-of-truth inputs) must be
  re-supplied at the start of the next session.

> **Definition of done for an iteration:** the deliverable is produced, the
> rubric was run, a dated Iteration Log entry exists, the backlog is current,
> the Spec/Changelog are in sync if a rule changed, and the memory is persisted.
> If any of those is missing, the iteration isn't done.

---

## Making the loop run automatically (enforcement)

Installing the skill is a **one-time** step, and so is `--init` per project. But
being installed does not by itself guarantee the loop runs every iteration —
skills are *model-invoked*, so the agent decides per task whether to consult
this skill, and it can under-trigger on a plain "add feature X" prompt. For
reliable, hands-off operation, wire the layer into the project so triggering
isn't left to chance. Two mechanisms, used together:

1. **`CLAUDE.md` pointer (always-loaded).** `probe.py --init` appends a short
   pointer (from `templates/CLAUDE.snippet.md`) to the project's `CLAUDE.md`.
   Because Claude Code loads `CLAUDE.md` into context at the start of every
   session, the agent is reminded on every task to read `.agent-eval/` first and
   update it before finishing. This is the highest-leverage, lowest-friction
   step.

2. **Claude Code hooks (deterministic).** `probe.py --install-hooks` merges two
   hooks into the project's `.claude/settings.json`, both handled by
   `hooks/agent_eval_hooks.py`:
   - **`SessionStart`** → injects the layer's status and the read/update
     instruction as context at the start of every session.
   - **`Stop`** → when a turn ends with uncommitted changes to files *outside*
     `.agent-eval/` but no update to `EVALUATION_LOG.md`, it asks the agent
     (via a `decision: block` continuation) to record the iteration before
     finishing. It is loop-safe (honors `stop_hook_active`), never fires on
     read-only/Q&A turns (no working-tree changes) or when git is unavailable,
     and can be silenced with the env var `AGENT_EVAL_ENFORCE=off`.

Do both with one command: `python <skill>/scripts/probe.py --init --with-hooks
--dir <project-root>`. Commit `CLAUDE.md` and `.claude/settings.json` so the
enforcement travels with the repo. After this, the user just develops normally
and the memory is written iteration by iteration without re-triggering anything.

---

## Bootstrapping a new project

When `.agent-eval/` doesn't exist yet:

1. Create the directory `.agent-eval/`.
2. Copy `templates/SPEC.template.md` → `.agent-eval/SPEC.md` and
   `templates/EVALUATION_LOG.template.md` → `.agent-eval/EVALUATION_LOG.md`
   (or run `python <skill>/scripts/probe.py --init --dir <project-root>`, which
   does the copy for you).
3. Fill in the Spec's **Purpose**, **Source of Truth**, initial **Rules &
   Regulations**, and a starter **Self-Review Rubric**. Derive these from: the
   user's stated goals, the repo's README / architecture, and obvious quality
   bars for the project's stack (e.g. tests pass, no secrets committed,
   accessibility, performance budgets — whatever fits the domain). Keep the first
   version small and true; the loop will grow it.
4. Write **Iteration Log Entry 1** describing the bootstrap and the initial
   ruleset, then commit.

Interview the user briefly if the purpose or the non-negotiable rules aren't
clear from context. A thin, honest Spec beats a bloated, speculative one.

---

## What counts as a "rule" worth versioning

Put something in the Spec (and log *why* in the Log) when it is a durable
constraint on how work is done, for example:
- a **rule** the user gave ("never fabricate content", "never delete an item
  from a list — reorder instead"),
- a **rubric** / quality gate (a checklist run before shipping),
- a **regulation** / policy (ATS-safety, licensing, data-handling, security),
- a **refinement** that fixed a real defect and should never regress.

One-off task details are *not* rules — they belong only in that iteration's Log
entry. Reserve the Spec for things that generalize across future iterations.

---

## Searchability conventions (so memory is findable, not just stored)

- **Every Iteration Log entry is dated and numbered** (`### Entry <N> — YYYY-MM-DD`).
  Numbers are stable and never reused.
- **Convert relative dates to absolute** when writing ("yesterday" → the actual
  date), so entries stay interpretable months later.
- **Tag entries with keywords** on a `Tags:` line (rule names, feature areas,
  defect types) so a plain text search across the file lands on the right entry.
- Refer to recurring topics with a stable slug in double brackets, e.g.
  `[[non-destructive-reorder]]`, so every mention of that topic is greppable.

---

## Hard rules for this skill (anti-patterns)

- **Never rewrite or delete Log history.** The Log is append-only. Correct a
  past mistake with a *new* entry that supersedes the old one, and cross-
  reference it — don't edit the old entry away.
- **Never let the Spec and the Log's Rules Changelog drift.** A rule change
  updates both, in th