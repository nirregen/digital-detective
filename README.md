# Digital Detective — Static Edition v0.6

A playable detective mystery built with **React + TypeScript + Vite**. A complete, deployable **static website** — no AI API, Docker, Python backend, database, accounts or secrets required.

## Quick start

```bash
cd frontend
npm install
npm run dev
```

Open the URL shown by Vite (usually http://localhost:5173).

## Deploy to Vercel

1. Commit this version on `feature/static-game-migration` and open a PR to `main`.
2. On Vercel, import the **frontend** Vite app, not the former FastAPI backend.
3. Select the folder containing `frontend/package.json` as **Root Directory** (usually `frontend`; some imports display a parent `digital-detective` folder, in which case pick `digital-detective/frontend`).
4. Framework: **Vite**. Build command `npm run build`. Output directory: `dist`.
5. No environment variables required. Deploy, then test a full investigation in an incognito browser.

If using the `Import single project` tile for `frontend`, Vercel generally selects the right root and framework automatically.

## Gameplay

- **The Last Message:** 3 suspects, 8 evidence items, 2 forensic puzzles, final verdict.
- **Branching interrogations:** each suspect has different scripted answers. New questions unlock when relevant evidence is collected; critical revelations require evidence.
- **Witness state:** trust/pressure and transcript recorded for each character.
- **Save system:** versioned browser `localStorage`; survives refreshes and tab changes in the same browser and origin. Reset case starts a new save.
- **Tests:** `cd frontend && npm test && npm run build`.

## Architecture

`frontend/src/main.tsx` → `frontend/src/game/engine.ts` → `frontend/src/data/case001.json` / `characters.json` → browser `localStorage`.

No network requests are needed by the game logic. Fonts are loaded from Google Fonts if available; system fonts provide fallback when offline.

### Trade-offs

- The complete case data, including puzzle answers and solution, is bundled into the browser. Players can inspect it using developer tools. This is acceptable for a **portfolio puzzle demo**, not a cheating-resistant paid game.
- Saves are per browser/device and do not sync. Clearing browser storage deletes progress.
- v0.5 SQLite saves are **not** migrated into browser storage. Existing development saves can remain in Docker volumes, but the static release starts a new case.
- Trust and pressure are persisted and shown, but scripted lines are currently fixed per choice; they do not yet produce multiple tone variants for all emotional states.

## Suggested enhancements

- Visual evidence board and pairwise deduction system
- More dialogue branches and mood-dependent replies
- Accessibility and E2E tests, save export/import
- Case authoring schema and multiple investigations

## Git history

The earlier AI / FastAPI / Docker prototype is preserved in Git history. The migration intentionally trades runtime AI for reliable, zero-setup public access.

All people, companies, and events are fictional.
