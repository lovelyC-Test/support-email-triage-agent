# Requirements — Customer Support Resolution Desk

What the system must do. Framed as MUST / SHOULD statements so anything not
listed here is out of scope until it lands in this file first.

## Functional requirements

### The seven actors

1. **Intake** — MUST clean incoming email (strip signatures, quoted reply
   chains, disclaimers). MUST extract `order_id` and `customer_id` where
   present. MUST reject empty or oversized messages (over
   `max_email_chars`, default 20,000) before any downstream call, with a
   logged reason.
2. **Classifier** — MUST return `category` ∈ {`refund`, `technical`,
   `general`}, plus `class_confidence` ∈ [0, 1] and a one-sentence
   `class_reason`. MUST be returned as a validated schema, never prose.
   SHOULD route to `general` and flag for review when
   `class_confidence < 0.5`.
3. **Refund agent** — MUST check order eligibility by date. If the order is
   not found MUST set the `order_not_found` flag and continue without
   inventing details.
4. **Technical agent** — MUST map the described symptom to a known fix.
   If nothing matches MUST say so explicitly in `findings`.
5. **General agent** — MUST default to marking as unanswerable rather than
   guessing.
6. **Composer** — MUST write a reply with citations to retrieved passages.
   MUST NOT add any claim not present in retrieved passages. If no chunks
   were retrieved MUST produce a stated non-answer, never fluent prose.
7. **Confidence gate** — MUST be deterministic Python; MUST NOT call a
   model. MUST combine four signals into a decision ∈ {`auto_reply`,
   `human_queue`}. Any missing signal MUST be treated as a fail.

### The four gate signals

All four MUST pass for `auto_reply`. Otherwise → `human_queue`.

1. `class_confidence` — MUST be ≥ `min_class_confidence` (default 0.6).
2. `retrieval_score` — MUST be ≥ `min_retrieval_score` (default 0.35).
3. `citation_count` — MUST be ≥ `min_citations` (default 1).
4. `flags` — MUST NOT contain any blocking flag (see below).

### Blocking flags (any one → escalate, regardless of other signals)

- `order_not_found` — refund request for a nonexistent order.
- `multi_intent` — email covers two categories at once.
- `legal_language` — mentions solicitor, lawsuit, regulator, or similar.
- `angry_tone` — abusive or threatening wording.

### The two exits

- **`auto_reply`** — the reply is sent, the run is logged.
- **`human_queue`** — the handover packet MUST contain: `draft_reply`,
  `retrieved_chunks` (sources), `category` + `class_reason`, `gate_reason`.
  A raw email alone is not a handover packet.

## Failure paths

Every one of these MUST be demonstrable:

- Retrieval returns nothing relevant → composer produces stated non-answer;
  gate escalates.
- Email covers two categories → `class_confidence` drops; `multi_intent`
  flag set; escalate.
- Order number does not exist → `order_not_found` flag; refund agent
  continues; escalate.
- Email is abusive or threatens legal action → `legal_language` or
  `angry_tone` flag; immediate escalation regardless of confidence.
- Oversized email (over `max_email_chars`) → rejected at the validator
  before any model call, with a logged reason.
- Entirely out-of-scope request → a clear refusal that names what the
  system does handle.
- Model provider is down → three retries with backoff; then a clean
  failure written to the ticket store.

## Non-functional requirements

- **Accuracy** — classifier accuracy ≥ 80% on the 20-item labelled set.
- **Cost** — total spend per run ≤ £0.40 (enforced by
  `LimitsConfig.max_spend_gbp_per_run`).
- **Loop caps** — every loop MUST have a cap and a test proving it holds.
- **Offline testable** — `make test` MUST pass with no network connection.
- **Grounding** — every factual claim in output MUST trace to something
  retrieved.
- **Auditability** — every node entry and exit MUST log with the trace id
  attached.
- **No secrets in repo history** — API keys and similar MUST live in
  `.env` (gitignored) or the environment, never in code or commits.

## Project constraints (the "seven rules")

Design constraints the whole codebase MUST honour:

1. An agent never calls an external service directly — it calls a tool.
2. A tool never calls a language model. Tools are dumb and deterministic.
3. Prompts live in files under `config/prompts/`, referenced by name.
4. The shared state is defined exactly once, in `state.py`, with types.
5. Every node takes the state and returns a *patch* — never mutates, never
   returns the whole state.
6. Configuration is loaded once at start-up into one settings object. No
   function anywhere else reads an environment variable.
7. Nothing prints. Everything logs, with the trace identifier attached.

## Definition of done

The project is finished when every one of these is true:

- A stranger can clone the repo, follow the README, and get a working run
  in ≤ 10 minutes.
- No secret appears anywhere in the repo history.
- `make test` passes, runs without a network connection, and covers
  routing, tools, and guardrails.
- Every loop has a cap and a test proving the cap is respected.
- Every factual claim in the output can be traced to something the system
  retrieved.
- There is a defined, demonstrated route by which the system declines and
  hands over to a person.
- `artifacts/runs/` contains at least three saved runs, including one
  deliberate failure.
- The evaluation set exists, has at least ten cases, and its results are
  recorded in the README.
- The README contains an architecture diagram, run instructions, known
  limitations, and the estimated cost per run.
