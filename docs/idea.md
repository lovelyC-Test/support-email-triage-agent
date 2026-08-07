# Idea — thought process notes

Personal sense-making before implementation. Kept as a scratch pad; the more
formal contracts and diagrams have graduated to `requirements.md` and
`architecture.md` in this folder.

## One-sentence problem
An incoming customer email is cleaned, sorted into one of three categories,
answered from the company's own help documents along a category-specific path,
and then judged: send the reply, or hand a prepared case to a human.

## Analogy from the project spec
A receptionist in a large building. They don't fix boilers or process refunds.
They work out, within ten seconds, which of three corridors you need, hand you
the right leaflet if the answer is on a leaflet, and walk you to a human when
it isn't. The intelligence is in the sorting and in the honesty about limits —
not in knowing everything.

## Self-check before touching code

Before implementing anything, be able to answer these without looking:

- What are the three categories, and what is each specialist's failure mode?
- What are the four gate signals and what makes each a "fail"?
- Which flags force escalation regardless of confidence?
- What is in the handover packet, and why is a raw email not enough?
- Why is the gate deterministic Python rather than a model call?

If any of those are fuzzy, re-read `requirements.md` before moving on.

Then read `architecture.md` for the flow diagram and worked examples.
