# Self-Review Rubric — reference menu

The Spec's Section 4 rubric should be **short and real** — six-ish checks you
actually run every iteration. This file is the menu to build that list from and
to grow it as the project matures. Copy the relevant items into the project's
`SPEC.md`; don't dump the whole menu in.

## Always-on core (start here)

- **Fidelity** — output grounded in the Source of Truth; nothing fabricated or invented.
- **Rule compliance** — every rule in Spec Section 3 was followed, checked by number.
- **Correctness** — does what was asked; obvious failure modes and edge cases checked.
- **Maintainability** — a future agent can read, understand, and extend it without tribal knowledge.
- **Human read** — natural and fit-for-user, not gamed to satisfy the rubric literally.
- **Memory hygiene** — this iteration is logged, backlog updated, Spec/Changelog in sync.

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

1. **Bootstrap:** take the *core* list plus 1–3 items from the domain sections
   that match the project's stack today. Keep it small.
2. **On each defect:** if a rubric miss keeps recurring, promote the specific
   check into the Spec rubric (and log why in the Evaluation Log).
3. **On each maturity step:** as the project heads toward production, pull more
   items from the engineering section into the active rubric.

A rubric item earns its place only if you'll actually run it. A long rubric that
gets skipped is worse than a short one that's honored every time.
