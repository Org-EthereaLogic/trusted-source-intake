# Constitution for Trusted Source Intake

This constitution defines the governing principles for this Chapter 1 repository.

## Scope

It applies to:

- the SQL intake pipeline and replay/quarantine logic,
- the Python contract-check and demo-metrics surfaces,
- Databricks bundle, job, and notebook walkthrough artifacts,
- sample data, tests, documentation, and governance artifacts.

## Required Decision Order

When principles conflict, resolve them in this order:

1. Safety and correctness.
2. Evidence traceability.
3. Security and secret hygiene.
4. Simplicity and proportionality.
5. Reproducibility and operational reliability.
6. Performance and speed.

## Governing Principles

### P1. Safety, Correctness, and Repository Integrity

- Never ship a change that knowingly violates acceptance criteria, policy boundaries, or repository integrity.
- Prefer explicit failure over silent unsafe behavior.
- Treat the checked-in intake rules, sample corpus, and chapter scope boundaries as hard constraints.

### P2. Evidence Traceability

- Every quality, replay, quarantine, and handoff claim must map to concrete evidence.
- Reports and docs must distinguish measured facts from interpretation.
- Missing evidence blocks completion claims.
- Functional PASS claims require replayable proof, not narrative assertion.

### P3. Security and Secret Hygiene

- No credentials, tokens, or secret material in repository content or committed artifacts.
- Use least-privilege credentials for any future Databricks validation.
- Treat secret exposure as a hard failure.

### P4. Simplicity and Proportionality

- Match implementation complexity to the size and risk of the problem.
- Prefer direct SQL and Python implementations over speculative framework layers.
- Avoid introducing broader platform abstractions not required by Chapter 1.

### P5. Reproducibility and Operational Reliability

- Keep sample data deterministic and the local demo replayable.
- Capture inputs, outputs, timestamps, and relevant metadata where the runtime supports it.
- Keep artifacts audit-friendly and explainable.

### P6. Public Method and Transparency Discipline

- This public repository may use standard public techniques and terminology.
- Proprietary UMIF formulas, internal scoring logic, or protected IP are prohibited.
- Do not imply hidden or undisclosed logic behind the chapter’s documented behavior.

### P7. Chapter Scope Discipline

- Chapter 1 proves trusted intake and ready-handoff control behavior only.
- It does not prove silent drift prevention, benchmark superiority, or live production Databricks execution.
- Do not widen claim scope beyond what the checked-in evidence supports.

## Related Documents

- `DIRECTIVES.md` defines enforceable repository rules.
- `AGENTS.md` defines operating behavior for coding agents.
- `SECURITY.md` defines the security policy.
- `README.md` and `docs/` define the chapter contract and evidence narrative.
