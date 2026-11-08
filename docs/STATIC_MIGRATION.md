# v0.6 static migration

- Preserve React UI and the authored Case 001 content.
- Replace `/api/*` calls with deterministic, typed functions in `frontend/src/game/engine.ts`.
- Replace free-form LLM questions with evidence-gated dialogue selections.
- Replace SQLite sessions with versioned `localStorage`.
- Remove backend, Compose and Ollama runtime dependencies from the release tree; keep history in Git.
- Do not market this as AI-powered runtime dialogue. AI can still support development and authoring.

**Manual release acceptance:** Complete both puzzles, recover E08, confront Alex with E02, refresh, switch witnesses, and reach the correct verdict. Confirm no `/api` requests are made in browser DevTools Network.
