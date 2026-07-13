# <Project Name> — Evaluation & Memory Log

**Purpose:** cross-session, cross-agent memory for this project. This file is
**append-only** — never delete history. It is how enhancements, fixes, new
rules, rubrics, regulations, and real user feedback compound across iterations
instead of resetting every session.

**Companion file:** `SPEC.md` (the current rules — this log explains *why* each
rule exists and tracks whether it's working).

## How any agent should use this file

1. **On session start:** read `SPEC.md` in full, then read this file's **Rules
   Changelog**, **Open Improvement Backlog**, and the **last 2–3 Iteration Log
   entries**.
2. **Do the requested work** per the Spec.
3. **Before ending the turn:** run the Spec's **Self-Review Rubric**, append a
   new **Iteration Log** entry, update the **Open Improvement Backlog**, and bump
   the Spec's **Version History** if any rule changed.
4. **If the user gives feedback** — positive or corrective — log it under that
   entry's "User feedback" field close to verbatim. Don't paraphrase away the
   specifics; future agents need the exact ask.
5. **Searchability:** every entry is dated, numbered, and tagged, so anyone
   (human or agent) can search this file for a date, rule name, or keyword and
   find the exact point it was introduced or changed.

## Rules Changelog

*(Mirrors the Spec's Version History, kept here too so rule history is
searchable alongside the reasoning/feedback that caused it. Newest first.)*

- **<YYYY-MM-DD>** — Added: <rule R# / rubric item / regulation>. Trigger:
  <what caused it>. See Entry <N>.

## Open Improvement Backlog

*(Unresolved defects or suggested next steps discovered during the Advisory
pass. Check off and move the reference into the relevant Iteration entry once
resolved — never silently delete.)*

- [ ] <Suggested improvement / latent defect / risk>. (Opened Entry <N>)

## Iteration Log

*(Newest entries appended at the bottom. Entry numbers are stable and never
reused.)*

### Entry 1 — <YYYY-MM-DD> — Bootstrap
- **Trigger:** Evaluation layer installed on <project>; initial Spec authored.
- **What happened:** Created `SPEC.md` (Purpose, Source of Truth, Rules R1..R#,
  Self-Review Rubric) and this log. Established `.agent-eval/` as committed memory.
- **Defects/weaknesses identified:** <none yet / list>.
- **Root cause:** <n/a for bootstrap>.
- **Lesson learnt:** <what to carry forward>.
- **User feedback (near-verbatim):** <"...">.
- **Rubric result:** <pass / which items failed>.
- **Suggested next improvement:** <first thing to harden>.
- **Tags:** bootstrap, setup

---

<!--
=== ITERATION ENTRY TEMPLATE — copy this block for each new iteration ===

### Entry <N> — <YYYY-MM-DD> — <short title>
- **Trigger:** <the brief / event that started this iteration>.
- **What happened:** <what was produced or changed, concisely>.
- **Defects/weaknesses identified:** <each rubric failure or issue found>.
- **Root cause:** <why it happened — one line per defect>.
- **Lesson learnt:** <the durable takeaway; promote to a Spec rule if it generalizes>.
- **User feedback (near-verbatim):** <"exact words, positive or corrective">.
- **Rubric result:** <pass, or list the items that failed and how they were resolved>.
- **Suggested next improvement:** <advisory-pass findings → also add to Backlog>.
- **Tags:** <keywords, rule names, [[topic-slug]]s for search>

-->

## Why memory works this way here
`SPEC.md` + this log **are** the memory. In a git project, `.agent-eval/` is
committed so `git pull` restores full context across sessions, machines, and
agents. In environments without automatic cross-session memory, re-supply both
files (and any source-of-truth inputs) at the start of every session — treat
that as step 1 of every future request.
