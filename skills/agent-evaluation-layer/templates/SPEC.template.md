# <Project Name> — System Specification

**Version:** 1.0
**Owner:** <name>
**Last updated:** <YYYY-MM-DD>
**Companion file:** `EVALUATION_LOG.md` (read both before doing any work)

> This is the *living contract* for how work is done on this project. It holds
> the current rules, rubrics, and regulations only. The **why** behind each rule,
> the defects that motivated it, and the record of every iteration live in the
> companion `EVALUATION_LOG.md`. Any agent picking up this project reads both.

## 1. Purpose

<One or two sentences: what this system/project is for, and the outcome a
correct piece of work produces. State the north star — e.g. "production-grade,
scalable, maintainable, top-tier quality" — in terms concrete to this project.>

## 2. Source of Truth

<What is authoritative for this project's content/behavior? e.g. the codebase +
tests, a master data file, an API contract, a design system. State what may NOT
be invented or contradicted, and what supersedes what when inputs conflict.>

## 3. Rules & Regulations

*(Numbered so the rubric and Log can reference them by number. Add rules over
time via the iteration loop; never renumber existing rules — append.)*

- **R1 — <rule name>.** <The rule, stated as an imperative constraint.>
  *(Added <date>; see Evaluation Log Entry <N> for rationale.)*
- **R2 — <rule name>.** <...>
- **R3 — <rule name>.** <...>

> Guidance: a good rule is durable (applies to future iterations, not just one
> task), testable (you can tell whether it was followed), and traceable (it
> points to the Log entry that explains why it exists).

## 4. Self-Review Rubric

*(Run at the END of every iteration. Each failing item becomes a Defect logged
in that iteration's entry. Keep this list short and real — every item must be a
check you actually perform. See `reference/rubric.md` for a menu to draw from.)*

- **Fidelity** — output is grounded in the Source of Truth; nothing fabricated.
- **Rule compliance** — every rule in Section 3 was followed, checked by number.
- **Correctness** — it does what was asked and the obvious failure modes were checked.
- **<Domain check>** — <e.g. tests pass / performance budget met / ATS-safe / a11y / no secrets committed>.
- **Maintainability** — a future agent can understand and extend this without tribal knowledge.
- **Human read** — it reads/behaves naturally for its end user, not gamed to the rubric.

## 5. Formatting & Delivery Standards

<Any standing conventions for how deliverables are produced and verified:
build/verify loop, file formats, naming, review steps, environments. Keep only
what generalizes across iterations.>

## 6. Governance & Memory

- Any material change to this Spec (new rule, correction, rubric, regulation)
  must be recorded in the **Version History** table below **and** explained with
  rationale in `EVALUATION_LOG.md` (Rules Changelog + the iteration entry).
- This Spec and `EVALUATION_LOG.md` together are the system's persistent memory.
- In a git repo, `.agent-eval/` is committed, so `git pull` restores full
  context. In environments without cross-session memory (e.g. Cowork), re-supply
  both files at the start of every session.

## Version History

| Version | Date | Change | Source |
|---|---|---|---|
| 1.0 | <YYYY-MM-DD> | Initial spec created for <project>. | Bootstrap (Evaluation Log Entry 1) |
