# support-email-triage-agent

Agentic email triage for customer support: classifies incoming messages into
three intents, answers from the company's own help documents via retrieval,
and escalates to a human when confidence is low.

> Status: scaffolding only. No implementation yet.

## Why

A small company receives around two hundred customer emails a week. Roughly
half are the same handful of questions — where is my order, how do I return
something, why has my subscription renewed. The other half are genuinely varied
and need a person. Today one member of staff reads all two hundred, which means
the difficult ones wait behind the easy ones.

Think of a receptionist in a large building. The receptionist does not know how
to fix a boiler or process a refund. What the receptionist does, extremely
well, is work out within ten seconds which of three corridors you need, hand
you the right leaflet if the answer is on a leaflet, and walk you to a human
when it is not. That is exactly what this system does. Its intelligence is in
the sorting and in the honesty about its own limits, not in knowing everything.

## Pipeline

1. **Classify** — assign the message to one of three categories. The model's
   output is a validated category, never free text.
2. **Route** — each category follows its own path through the graph.
3. **Retrieve** — search the company's help documents before answering
   anything, and detect when retrieval was too weak to answer from.
4. **Gate** — decide whether the answer is good enough to send on its own.
5. **Hand over** — when it is not, escalate with the full context the human
   needs, not just the original message.

The confidence gate in step 4 is the heart of the project.

## Layout

```
src/triage_agent/
├── api/              HTTP entrypoint (request/response schemas, routes)
├── agent/
│   ├── nodes/        one module per graph node (classify, retrieve, answer, gate, handover)
│   ├── routes/       the conditional edges — which path each category takes
│   └── prompts/      prompt templates, versioned as files rather than inline strings
├── retrieval/        document loading, chunking, indexing, search
├── clients/          LLM / vector store / mail adapters behind interfaces (so tests can mock them)
├── config/           env-driven settings, thresholds, category definitions
└── observability/    tracing, token and cost logging, decision audit trail

data/
├── help_docs/        the source knowledge base (contents gitignored)
└── samples/          example emails for local runs

evals/
├── datasets/         labelled test sets — the classifier set and the gate set
└── reports/          generated confusion matrices and metrics (gitignored)

tests/
├── unit/             pure logic, LLM calls mocked
└── integration/      end-to-end graph runs

scripts/              CLI entrypoints (ingest docs, run eval, replay an email)
docs/                 architecture notes and decision records
```

## Evaluation

Two things get measured separately:

- **Classifier** — a confusion matrix built from a labelled test set, not an
  impression of how it feels.
- **Confidence gate** — the trade-off between sending wrong answers and
  escalating easy ones. The number that matters most is the false-confident
  rate: how often it answered when it should have escalated.

## Setup

```bash
cp .env.example .env    # then fill in your keys — .env is gitignored
```
