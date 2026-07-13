# <Project Name> — Evaluation & Memory Log

**Purpose:** a cross-session, cross-agent, **append-only** history of *why* this
project changed the way it did — the defects, root causes, lessons, and real user
feedback behind each iteration. It exists so that knowledge compounds across
sessions instead of resetting every time.

> **This file is NOT a rules file.** It never states "the current rules are X".
> Your project's own docs (e.g. `CLAUDE.md`, a README, an ADR folder) remain the
> single source of truth for the *current* rules and behavior. This log only
> records the dated *history* — what happened and why — which those snapshot
> docs deliberately don't keep. Keeping the two separate is the whole point:
> there is never a second "current rules" file to drift out of sync.

## How to use this file

1. **On session start (for context):** skim this file's **Open Improvement
   Backlog** and the **last 2–3 Iteration Log entries** so you know what recently
   changed and why. (The *current* rules still come from the project's own docs.)
2. **Do the requested work** the way the project's own docs prescribe.
3. **At a checkpoint** — a feature tested and confirmed done, a bug root-caused
   and fixed, or before switching sessions/agents — append a new **Iteration Log**
   entry and update the **Open Improvement Backlog**. One entry per independent,
   reproducible lesson (not one giant entry per session).
4. **If the user gives feedback** — positive or corrective — record it under that
   entry's "User feedback" field close to **verbatim**. Don't paraphrase away the
   specifics; a future agent needs the exact ask.
5. **Searchability:** every entry is dated, numbered, and tagged, so anyone (human
   or agent) can search this file for a date, keyword, or `[[topic-slug]]` and land
   on the exact point something was introduced or changed.

## Decisions & Rules History

*(A dated **index of when and why** a durable rule or decision was adopted —
newest first. This is history, not the rule itself: write the actual current rule
into the project's own docs, e.g. `CLAUDE.md`, and leave a one-line pointer here.
Because every line is a timestamped past event that is never edited, it cannot
drift out of sync with the project's live rules.)*

- **<YYYY-MM-DD>** — Adopted: <short name of the rule/decision>. Why: <the defect
  or reason that triggered it>. Current rule lives in: <e.g. `CLAUDE.md` §X>. See
  Entry <N>.

## Open Improvement Backlog

*(Unresolved defects, risks, or suggested next steps surfaced during an iteration.
Check an item off and move its reference into the resolving Iteration entry once
done — never silently delete.)*

- [ ] <Suggested improvement / latent defect / risk>. (Opened Entry <N>)

## Iteration Log

*(Newest entries appended at the bottom. Entry numbers are stable and never
reused. Append-only — never rewrite a past entry; supersede it with a new one and
cross-reference.)*

### Entry 1 — <YYYY-MM-DD> — Bootstrap
- **Trigger:** Evaluation layer installed on <project>; memory log created.
- **What changed:** Created `.agent-eval/EVALUATION_LOG.md` as the project's
  committed, append-only history. (No rules file is created — the project's own
  docs remain the source of truth for current rules.)
- **Defects/weaknesses identified:** <none yet / list>.
- **Root cause:** <n/a for bootstrap>.
- **Lesson learnt:** <what to carry forward>.
- **User feedback (near-verbatim):** <"...">.
- **Self-review notes:** <optional — anything you checked and what you found>.
- **Suggested next improvement:** <first thing to harden → also add to Backlog>.
- **Tags:** bootstrap, setup

---

<!--
=== ITERATION ENTRY TEMPLATE — copy this block for each new iteration ===

### Entry <N> — <YYYY-MM-DD> — <short title>
- **Trigger:** <the brief / event that started this iteration>.
- **What changed:** <what was produced or changed, concisely>.
- **Defects/weaknesses identified:** <each issue found>.
- **Root cause:** <why it happened — one line per defect>.
- **Lesson learnt:** <the durable takeaway. If it generalizes into a rule, write
  the rule into the project's own docs (e.g. CLAUDE.md) and add a dated pointer
  under "Decisions & Rules History" above>.
- **User feedback (near-verbatim):** <"exact words, positive or corrective">.
- **Self-review notes:** <optional — checks you ran (see reference/rubric.md for a
  menu) and what they turned up>.
- **Suggested next improvement:** <findings → also add to the Backlog>.
- **Tags:** <keywords, [[topic-slug]]s for search>

-->

## Why memory works this way here

This log **is** the memory of *why*. In a git project, `.agent-eval/` is committed
so `git pull` restores full history across sessions, machines, and agents. It is
deliberately kept separate from — and never duplicates — the project's own
current-rules docs (`CLAUDE.md`, READMEs, ADRs): those say what the rules *are
now*; this says how they *got that way*. In environments without automatic
cross-session memory, re-supply this file at the start of a session to restore
context.
