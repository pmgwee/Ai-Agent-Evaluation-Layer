<!-- agent-evaluation-layer:start -->
## Agent Evaluation Layer (memory & iteration refinement)

This project uses the **agent-evaluation-layer** skill. Its persistent memory lives in `.agent-eval/`:

- `.agent-eval/SPEC.md` — current rules, rubrics, and regulations (versioned).
- `.agent-eval/EVALUATION_LOG.md` — append-only memory: user feedback, defects, lessons learnt, improvement backlog.

**On every task in this project:**

1. **Start** by reading `.agent-eval/SPEC.md` in full and the last 2–3 Iteration Log entries in `.agent-eval/EVALUATION_LOG.md`.
2. **Do the work** strictly per the Spec's rules.
3. **Before finishing**, run the Spec's Self-Review Rubric, then append a dated Iteration Log entry recording: what changed, defects found + root cause, lesson learnt, user feedback (near-verbatim), the rubric result, and a suggested next improvement. Update the Open Improvement Backlog, and bump the Spec's Version History if any rule/rubric/regulation changed.
4. **Commit** `.agent-eval/` together with your changes: `git add .agent-eval && git commit -m "eval: iteration <N> — <summary>"`.

Rules: the Log is **append-only** — never rewrite or delete past entries; supersede with a new one. Keep the Spec's Version History and the Log's Rules Changelog in sync. Full loop and rationale: see the `agent-evaluation-layer` skill's `SKILL.md`.
<!-- agent-evaluation-layer:end -->
