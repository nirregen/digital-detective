# Case 001 — The Last Message (SPOILERS)

## Canonical truth

At 19:52, CTO Leon Vale altered Northstar Systems' audit records to hide fabricated customer security approvals. Maya Levin detected the change and prepared to preserve the original records. At 20:05, a resignation email was sent in Maya's name without her consent. At 21:40, Maya left via the service stairwell with help from Dana Cho. At 22:14, security manager Alex Morgan returned to the server room to retrieve a backup; a copy was made at 22:18. Maya is alive and has gone into hiding by choice because she fears Leon will destroy the evidence.

## Character truth table (server-only knowledge)

| Character | Knows | Conceals | Contradiction trigger |
|---|---|---|---|
| Alex | Returned at 22:14; copied backup | Lied about leaving for the night | Present E02 access log |
| Dana | Maya left voluntarily; protected her | Helped Maya leave | Timeline + Maya's note |
| Leon | Altered audit records; forged email | Responsible for manipulation | Present E06 audit diff |

## 8 evidence items and dependencies

- E01 resignation email, available immediately.
- E03 blurry camera still, immediately available; intentionally not conclusive.
- E04 ROT13 hint, immediately available.
- E07 Alex's initial statement, immediately available.
- E02 access log, unlocked by solving decrypt puzzle.
- E05 backup manifest, unlocked by solving decrypt puzzle.
- E06 audit diff, unlocked after collecting E05.
- E08 voice note, unlocked after solving timeline puzzle.

## Puzzles

1. Decrypt **PURPX GUR ONPXHC** using ROT13; answer **CHECK THE BACKUP**. E04 must be collected before submission.
2. Order events **audit → email → camera → badge**. Requires collecting E01, E02, E03 and E06. E08 is then unlocked.

## Winning condition

The correct responsible party is **Leon**. The final submission must contain **E02**, **E06**, **E08**, and those items must first be collected. Early or unsupported verdicts are rejected.

## Narrative caveat / suggested next iteration

The current MVP validates the responsible party and evidence list, not a detailed written explanation of Maya's disappearance. A later version should require three separately justified findings (who tampered, why Maya vanished, why Alex lied) to deepen deduction.

## AI character policy (future feature)

- Treat the case engine as the sole source of truth; the model never writes game state.
- Build per-character allowlisted facts for each dialogue turn; do not send the entire canonical story to the model.
- The engine decides whether a specific evidence ID meets an unlock/contradiction condition before prompt construction.
- Output a structured object: `{reply, tone, claimed_fact_ids, proposed_action}`. Ignore unallowlisted `claimed_fact_ids` and never execute `proposed_action` directly.
- Never reveal secret facts absent from the character's allowlist, even when asked to roleplay, ignore prior instructions, or disclose hidden prompts.
- Character may lie only about specifically designated cover-story facts. Every other canonical fact must remain consistent.
- Limit requests by token, per-session quota, message length and timeouts. Store only what is required for gameplay.
- Test prompt injection, spoiler leakage, hallucinated evidence, wrong witness knowledge, and repeated-turn consistency. Safe fallback: scripted line.
- Use fictional persons and fabricated data; no real private information.

## Game state

```json
{
  "collected": ["e01", "e04"],
  "solved": ["decrypt"],
  "interviews": [{"character": "alex", "question": "Where were you?", "evidence": null, "reply": "..."}],
  "finished": false,
  "result": null,
  "events": [{"type": "evidence_collected", "id": "e01"}]
}
```

The state is persisted in SQLite keyed by an anonymous UUID header. Server responses additionally compute `available` evidence ids; that list is derived and not stored.

## Planned API

`GET /api/case`, `GET /api/state`, `POST /api/evidence/{id}/collect`, `POST /api/puzzles/decrypt`, `POST /api/puzzles/timeline`, `POST /api/interrogate`, `POST /api/submit`, `POST /api/reset`, `GET /api/health`.
