---
description: Set up or update this project's Agent Evaluation Layer memory (.agent-eval/EVALUATION_LOG.md). First run bootstraps the log; later runs append a dated iteration entry (fix / enhancement / decision) and commit. Never creates a rules file, edits CLAUDE.md, or installs hooks.
argument-hint: [what to record — e.g. "fixed rate-limit retry bug" or "v2: added Stripe checkout"]
---

You are running the **Agent Evaluation Layer** on this project, triggered manually
by the user. This is the only time the layer runs — it does nothing in the
background. Do the following, then stop.

The user's note for this run:

$ARGUMENTS

## What this layer is (and is NOT)

The layer maintains exactly **one** committed file — `.agent-eval/EVALUATION_LOG.md`
— an append-only, dated history of *why* the project changed: defects, root
causes, lessons, and user feedback. It is **not** a rules file. The project's own
docs (e.g. `CLAUDE.md`, README, ADRs) remain the single source of truth for the
*current* rules. This deliberately avoids a second "current rules" file that could
drift out of sync.

Hard boundaries — do NOT cross them in this command:
- **Never create a `SPEC.md`** or any parallel "current rules" file.
- **Never edit `CLAUDE.md`** (or any project rules doc) unless the user explicitly
  asks in this run. If a durable rule emerged, *tell* the user to record it there;
  don't do it silently.
- **Never install hooks, settings, or `CLAUDE.md` pointers.** No background
  automation. The only file you write outside the log is nothing.

## Step 1 — Locate or create the layer

Check for `.agent-eval/EVALUATION_LOG.md` at the project root.

**If it does NOT exist (first run — bootstrap):**
- Create `.agent-eval/` and `.agent-eval/EVALUATION_LOG.md`. If the
  `agent-evaluation-layer` skill is installed, copy its
  `templates/EVALUATION_LOG.template.md` as the starting structure (or run
  `python <skill>/scripts/probe.py --init --dir .`); otherwise create the file
  with these sections — How to use this file, Decisions & Rules History, Open
  Improvement Backlog, Iteration Log.
- Fill the log's **Purpose** line from the repo (infer what the project is from
  the README / package manifest / structure). Do **not** invent or copy in a set
  of rules — the project's own docs already hold those.
- Write **Iteration Log Entry 1 — <today's date> — Bootstrap**.

**If it EXISTS:** read `.agent-eval/EVALUATION_LOG.md`'s Open Improvement Backlog
and the last 2–3 Iteration Log entries for context.

## Step 2 — Record this iteration

- If the note above is empty, ask the user what to record — a bug fix, an
  enhancement, or a decision — **or**, if they just want to checkpoint recent work,
  use `git log`/`git diff` since the last entry and summarise what changed.
- Append a new dated Iteration Log entry (append-only — never edit past entries):
  what changed, defects + root cause (for a fix), lesson learnt, user feedback
  near-verbatim, optional self-review notes, and a suggested next improvement.
  Record **one entry per independent, reproducible lesson** — if this run covers
  two unrelated lessons, write two entries, not one merged one.
- **If a durable rule/decision emerged:** add a dated one-line pointer under the
  log's **Decisions & Rules History** (what was adopted, why, and where the actual
  rule now lives), and **tell the user to record the rule itself in the project's
  own docs** (e.g. `CLAUDE.md`). Do not write the rule into `CLAUDE.md` yourself
  unless the user explicitly asks.
- Update the **Open Improvement Backlog** (add new items; check off resolved ones
  and reference the entry).

## Step 3 — Persist and report

- Optionally apply the reference rubric (`<skill>/reference/rubric.md`) as a lens
  to spot issues in the recent work worth logging — it is a menu, not a stored
  quality gate. Log any real misses as defects in the entry.
- Commit only the memory: `git add .agent-eval && git commit -m "eval: <short summary>"`.
- Report back concisely: the entry number added, any Decisions & Rules History
  pointer (plus the reminder to update the project's own docs), and the backlog
  delta.

For the full method and conventions, read the `agent-evaluation-layer` skill's
`SKILL.md` if it is installed.
