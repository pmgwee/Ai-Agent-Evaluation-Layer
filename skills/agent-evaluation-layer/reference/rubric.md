# Self-Review Rubric — reference menu

An **optional lens** the `/agent-evaluation-layer` run can apply to the recent work to surface issues
worth logging. It is a menu to pick from — **not** a stored quality gate and not a
rules file. Nothing here is persisted into the project; the project's own docs
(e.g. `CLAUDE.md`) remain the source of truth for actual standards. Use a handful
of the checks below at eval time, and log any real miss as a defect in the
iteration entry.

## Always-on core (start here)

- **Fidelity** — output grounded in reality (the code/tests/data); nothing fabricated or invented.
- **Consistency with project rules** — the work matches the project's own docs (e.g. `CLAUDE.md`, README, ADRs).
- **Correctness** — does what was asked; obvious failure modes and edge cases checked.
- **Maintainability** — a future agent can read, understand, and extend it without tribal knowledge.
- **Human read** — natural and fit-for-user, not gamed to satisfy a check literally.
- **Memory hygiene** — this iteration is logged and the backlog is updated.

## Engineering / production-grade (pull in as the system scales)

- **Tests** — automated tests exist for changed behavior and pass; new logic has coverage.
- **Error handling** — failures are handled and surfaced, not swallowed; no unhandled rejections.
- **Security** — no secrets committed; inputs validated; authz/authn boundaries respected; deps free of known criticals.
- **Performance** — meets the project's budget (e.g. LCP/FCP/CLS targets, query latency, token cost); no obvious regressions.
- **Reliability & scale** — handles rate limits, retries, idempotency, and concurrency for the expected load.
- **Observability** — meaningful logs/metrics/traces for the new path; failures are diagnosable in prod.
- **Data integrity** — migrations are reversible; no destructive change without a backup/confirmation path.
- **Accessibility** — semantic structure, keyboard reachable, sufficient contrast (for user-facing UI).
- **Docs** — README / API docs / changelog updated so the change is discoverable.
- **Rollback** — there is a safe way to undo this change in production.

## Agent / LLM-system specific (for RAG, agents, prompt pipelines)

- **Grounding & citations** — answers cite sources; claims are traceable to retrieved context.
- **Retrieval quality** — the right context is retrieved (recall/precision spot-checked on real queries).
- **Prompt/version pinning** — model, prompt, and tool versions are recorded so results are reproducible.
- **Token/cost budget** — cost per request within target; no runaway loops.
- **Self-correction** — the agent detects and recovers from its own bad outputs (grading, re-query, guardrails).
- **Determinism where it matters** — critical paths don't depend on nondeterministic output without a check.

## How to use this menu

1. **Per iteration:** run the *core* list plus 1–3 items from the domain sections
   that match the project's stack today. Keep it light — this is a lens for finding
   things worth logging, not a gate to pass.
2. **On a recurring miss:** if the same check keeps failing, that's a durable
   lesson — write the rule into the project's own docs (e.g. `CLAUDE.md`) and leave
   a dated pointer under the log's Decisions & Rules History.

A check earns its place only if you'll actually run it. A long rubric that gets
skipped is worse than a short one that's honored every time.
