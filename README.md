# support-desk

**Project 1 — Customer Support Resolution Desk.** Routing and retrieval with a
confidence gate controlling the exit.

An incoming email is cleaned, classified into one of three categories, routed
down a matching path, answered from the company's own help documents, and then
judged: is this answer good enough to send on its own, or does it need a human?

That last decision — the confidence gate — is the heart of the project.

## Setup

Python 3.12 or newer. No API key needed until phase 6.

```bash
make install          # venv, dependencies, pre-commit hooks
cp .env.example .env  # add OPENAI_API_KEY when you reach phase 6
make check            # lint, typecheck, tests
make version          # phase 1 acceptance test
```

## Commands

```bash
make lint         # ruff check --fix, then ruff format
make typecheck    # mypy, strict
make test         # pytest
make check        # all three, as CI would
make help         # list every target
```

## Layout

Follows Project 1 §1.7 and the standard skeleton in Part 1 §1.3. Modules for
later phases exist but are empty, holding a one-line docstring stating their job.

```
config/settings.yaml          models, limits, memory, gate thresholds
config/prompts/*.md           one prompt per agent, version controlled
src/support_desk/
  main.py                     CLI: process one email or a whole folder
  config.py                   loads settings.yaml + .env into one object
  state.py                    SupportState, defined exactly once
  graph.py                    nodes and edges; no business logic
  agents/                     intake, classifier, refund, technical, general, composer
  tools/                      order_lookup, policy_lookup. A tool never calls a model
  memory/                     vector_store (Chroma), ticket_store (SQLite)
  models/                     gateway.py (the only LLM caller), schemas.py
  guardrails/                 gate.py, validators.py, limits.py. Nothing calls a model
  utils/                      logging.py, tokens.py
data/raw/help_articles/       30-50 short help articles (phase 3)
data/raw/emails/              40 sample emails, 20 labelled (phase 3)
data/index/                   Chroma persistent directory (phase 5)
artifacts/runs/               one folder per run: state, log, outputs
scripts/                      build_index, seed_db, run_eval
tests/unit  tests/integration  tests/fixtures
app/streamlit_app.py          the demonstration interface (phase 8)
```

## The seven rules

From Part 1 §1.4. Each exists because breaking it causes a specific problem later.

1. An agent never calls an external service directly — it calls a tool.
2. A tool never calls a language model. Tools are dumb and deterministic.
3. Prompts live in files under `config/prompts/`, referenced by name.
4. The shared state is defined exactly once, in `state.py`, with types.
5. Every node takes the state and returns a *patch* — never mutates, never
   returns the whole state.
6. Configuration is loaded once at start-up into one settings object. No function
   anywhere else reads an environment variable.
7. Nothing prints. Everything logs, with the trace identifier attached.

## Current state

Phase 1 complete, phase 2 in progress.

Every function is a signature, a docstring explaining what it must do, and
`raise NotImplementedError`. Writing the bodies is the exercise. Declarations are
finished and need no work: `state.py`, `models/schemas.py`, and the settings
classes in `config.py`.

### Now: phase 2 — plumbing

> Acceptance test: *a test replaces the gateway with the fake and passes offline.*

In dependency order:

1. `resolve_path()` in `config.py`
2. `get_settings()` in `config.py` — the one with real substance
3. `configure()`, `get_logger()`, `bind_run()` in `utils/logging.py`
4. `FakeGateway.__init__` and `.structured()` in `models/gateway.py`
5. `build_parser()` and `main()` in `main.py`

Leave `ModelGateway` unimplemented for now — it needs an API key and phase 6.

Un-skip the tests in `tests/unit/test_config.py` and `tests/unit/test_gateway.py`
as each starts passing. They are written as a checklist; each name states what it
proves.

Done when `make check` is green and `make version` prints `0.1.0`.

## Build sequence

Project 1 §1.10, which refines the eight-phase method in Part 1 §1.11.

1. **Scaffold** — folders, empty modules, README, first commit *(done)*
2. **Plumbing** — config, logging, gateway, FakeGateway ← *here*
3. **Data** — 30-50 help articles, 40 emails, 20 hand-labelled
4. **State and stubs** — every node returns a fixed patch; all three routes run
5. **Retrieval** — build the index; five hand-written retrieval checks
6. **Classifier** — real prompt, confusion matrix, above 80% accuracy
7. **Specialists and composer** — every reply cites a source or declines
8. **Gate** — four signals, exhaustively tested. The most important file here
9. **Exits** — send and escalate; the handover packet
10. **Interface** — Streamlit inbox showing the gate's reasoning

## Notes on cost

Both model roles are set to `gpt-4o-mini` in `config/settings.yaml`. Phases 1-5
cost nothing, because everything runs against `FakeGateway`. Real spend starts at
phase 6, at roughly a tenth of a penny per email through the full graph.

While iterating on prompts, evaluate against 5 emails rather than 20 and save the
full labelled set for the number that goes in this README.
