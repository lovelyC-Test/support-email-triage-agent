# support-desk

**Project 1 — Customer Support Resolution Desk.** Routing and retrieval with a
confidence gate controlling the exit.

An incoming email is cleaned, classified into one of three categories, routed
down a matching path, answered from the company's own help documents, and then
judged: is this answer good enough to send on its own, or does it need a human?

That last decision — the confidence gate — is the heart of the project.

## Setup

Python 3.12 or newer. No API key needed until the classifier phase.

```bash
make install          # venv, dependencies, pre-commit hooks
cp .env.example .env  # add OPENAI_API_KEY when the real gateway lands
make check            # lint, typecheck, tests
```

## Commands

```bash
make lint         # ruff check --fix, then ruff format
make typecheck    # mypy, strict
make test         # pytest
make check        # all three, as CI would
make help         # list every target
```

## Documentation

- `docs/idea.md` — sense-making notes: problem, analogy, self-check.
- `docs/requirements.md` — what the system must do (MUST/SHOULD, gate
  signals, blocking flags, failure paths, non-functional requirements,
  project constraints, definition of done).
- `docs/architecture.md` — how it's put together (flow diagram, shared
  state, tech stack, folder layout, end-to-end worked examples).

## Current state

Phase 2 in progress — plumbing.

> Acceptance test: *a test replaces the gateway with the fake and passes offline.*

Every function is a signature, a docstring explaining what it must do, and
`raise NotImplementedError`. Writing the bodies is the exercise. Declarations
are finished: `state.py`, `models/schemas.py`, and the settings classes in
`config.py`.

In dependency order:

1. `resolve_path()` in `config.py`
2. `get_settings()` in `config.py` — the one with real substance
3. `configure()`, `get_logger()`, `bind_run()` in `utils/logging.py`
4. `FakeGateway.__init__` and `.structured()` in `models/gateway.py`
5. `build_parser()` and `main()` in `main.py`

Leave `ModelGateway` unimplemented for now — it needs an API key and a
later phase.

Un-skip the tests in `tests/unit/test_config.py` and `tests/unit/test_gateway.py`
as each starts passing. They are written as a checklist; each name states what
it proves.

Done when `make check` is green and `make version` prints `0.1.0`.

## Notes on cost

Everything runs against `FakeGateway` until the classifier phase, so it costs
nothing. Real spend starts once the model gateway is wired to a provider, at
roughly a tenth of a penny per email through the full graph.

While iterating on prompts, evaluate against 5 emails rather than 20 and save
the full labelled set for the number that goes in this README.
