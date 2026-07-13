---
description: Set up or update this project's Agent Evaluation Layer memory (.agent-eval/). First run bootstraps it; later runs record a fix / enhancement / rule into memory and commit.
argument-hint: [what to record — e.g. "fixed rate-limit retry bug" or "v2: added Stripe checkout"]
---

You are running the **Agent Evaluation Layer** on this project, triggered manually
by the user. This is the only time the layer runs — it does nothing in the
background. Do the following, then stop.

The user's note for this run:

$ARGUMENTS

## Step 1 — Locate or create the layer

Check for a `.agent-eval/` directory at the project root.

**If it does NOT exist (first run — bootstrap):**
- Create `.agent-eval/`, then create `.agent-eval/SPEC.md` and
  `.agent-eval/EVALUATION_LOG.md`. If the `agent-evaluation-layer` skill is
  installed, copy its `templates/SPEC.template.md` and
  `templates/EVALUATION_LOG.template.md` as the starting structure (or run
  `python <skill>/scripts/probe.py --init --dir .`); otherwise create the two
  files with these sections — SPEC: Purpose, Source of Truth, Rules &
  Regulations (R1..), Self-Review Rubric, Version History; LOG: How to use,
  Rules Changelog, Open Improvement Backlog, Iteration Log.
- Seed the Spec from the repo: infer **Purpose** and **Source of Truth** from the
  README / package manifest / project structure, and propose 2–4 starter **Rules**
  plus a short **Self-Review Rubric** that fit this stack. Ask the user at most
  1–2 quick questions, and only if Purpose or a critical rule is genuinely
  unclear — otherwise proceed with sensible defaults they can refine later.
- Write **Iteration Log Entry 1 — <today's date> — Bootstrap**.

**If it EXISTS:** read `.agent-eval/SPEC.md` in full and the last 2–3 Iteration
Log entries in `.agent-eval/EVALUATION_LOG.md`.

## Step 2 — Record this iteration

- If the note above is empty, ask the user what to record — a bug fix, an
  enhancement, a new rule/rubric/regulation, or feedback — **or**, if they just
  want to checkpoint recent work, use `git log`/`git diff` since the last entry
  and summarise what changed.
- Append a new dated Iteration Log entry (append-only — never edit past entries):
  what changed, defects + root cause (for a fix), lesson learnt, user feedback
  near-verbatim, rubric result, and a suggested next improvement.
- If the note introduces a **durable rule / rubric / regulation**, add it to the
  Spec's Rules section and bump the Spec **Version History** + the Log's **Rules
  Changelog** (keep them in sync).
- Update the **Open Improvement Backlog** (add new items; check off resolved ones
  and reference the entry).

## Step 3 — Persist and report

- Run the Spec's Self-Review Rubric against the recent work; log any misses as
  defects in the entry.
- Commit only the memory: `git add .agent-eval && git commit -m "eval: <short summary>"`.
- Report back concisely: the entry number added, any rule/version change, and the
  backlog delta.

For the full method and conventions, read the `agent-evaluation-layer` skill's
`SKILL.md` if it is installed. Do not set up hooks or edit `CLAUDE.md` unless the
user explicitly asks for the optional automatic mode.
