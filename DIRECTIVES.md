# Trusted Source Intake Directives

These directives are enforceable rules for humans and agents working in this repository.

## CRITICAL

- **No placeholders**: do not add TODO, FIXME, TBD, XXX, or template brackets.
- **No secrets**: never commit credentials, tokens, passwords, private endpoints, or workspace secrets.
- **No hidden dependencies**: implementation and verification dependencies must be declared in repo-managed config or clearly documented.
- **No claim inflation**: do not describe the checked-in sample as more than it is. This repo models one intake domain over four sample batches, not a verified multi-source enterprise deployment.
- **No silent rule drift**: SQL quarantine logic and Python contract logic must stay semantically aligned.
- **No destructive artifact mutation**: do not rewrite checked-in demo outputs or sample inputs to hide failures.
- **Public-method discipline**: standard public methods are allowed; proprietary UMIF formulas or hidden IP-bearing logic are prohibited.

## IMPORTANT

- Keep README, docs, notebooks, and sample outputs aligned with the current executable demo.
- Distinguish local demo evidence from live Databricks execution evidence.
- Preserve deterministic sample data and reproducible counts.
- Keep the bundle and job configs consistent with the repo layout.

## RECOMMENDED

- Add tests for any new contract rule or replay edge case.
- Keep naming identical across SQL, Python, docs, and notebook walkthroughs.

## Verification Commands

```bash
pip install -e ".[dev]"
PYTHONPATH=src python -m pytest -q
python -m ruff check src tests
PYTHONPATH=src python -m intake.demo_metrics
```

Optional when approved workspace credentials exist:

```bash
databricks bundle validate --target dev
databricks bundle validate --target prod
```
