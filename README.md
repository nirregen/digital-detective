# Digital Detective — The Last Message

**An interactive mystery game with a deterministic investigation engine and an AI-ready dialogue layer.**

## Start with Docker

```bash
docker compose up --build
```

Open **http://localhost:5173**. API docs are at **http://localhost:8000/docs**.

### Local development without Docker

Backend (from repository root):

```bash
python -m venv .venv
# activate .venv for your shell
pip install -r backend/requirements.txt
PYTHONPATH=backend uvicorn app.main:app --reload --port 8000
```

Frontend (a separate terminal):

```bash
cd frontend
npm install
npm run dev
```

The Vite proxy defaults to `http://localhost:8000` for local development; Docker Compose overrides it to `http://backend:8000`.

## Features in 0.1

- Case 001 — *The Last Message*, 3 suspects, 8 evidence items, 2 puzzles.
- Locked evidence gating and server-authoritative state.
- Scripted witness interrogation with proof-driven contradictions.
- SQLite persistence for each anonymous browser session.
- Final verdict that checks all required evidence.
- Automated backend tests and GitHub Actions CI.

## Architecture

React / TypeScript (Vite) → REST API (FastAPI) → game rules → SQLite. `cases/case_001.json` is the content source. No AI provider is required at this stage; witness dialogue uses a deterministic adapter to make game testing reliable.

## Non-goals / known limitations

- This MVP does **not** include an actual LLM integration, login, multiplayer, streaming chat, or security-hardened public deployment.
- Session UUIDs in localStorage are anonymous identifiers, **not authentication**. Do not deploy the current write API publicly without rate limiting, authentication and further hardening.
- Puzzle answers are validated server side; the case content file includes spoilers and should not be bundled directly into the browser.
- Case data is fixed; the case creator will come in a later version.

## Tests

```bash
pip install -r backend/requirements.txt
PYTHONPATH=backend pytest -q backend/tests
```

## Next milestones

1. Make interrogations contextual using a constrained AI adapter and structured JSON outputs.
2. Introduce content schema validation for custom cases.
3. Add an evidence board, inventory-driven dialogue, hint engine, and end-to-end tests.
4. Add auth, abuse controls, deployment, tracing and monitoring.

All people and organizations in this game are fictional.


## Local AI interrogations (Ollama)

This version is preconfigured for a model running on **the Windows host**, not inside Docker.

1. Install Ollama on Windows and download: `ollama pull qwen3:4b`.
2. Test from PowerShell: `ollama list` and `curl.exe http://localhost:11434/api/tags`.
3. From the project directory: `docker compose up --build -d`.
4. Visit `http://localhost:8000/api/ai-status` (should say `ollama`) and `http://localhost:5173` to interrogate witnesses.
5. Monitor logs: `docker compose logs -f backend`. If Ollama can't be reached, the script falls back to fixed replies.

If you use a different installed model, change `OLLAMA_MODEL` in `docker-compose.yml` to the exact name returned by `ollama list`. The first generated response can be slow.

**Privacy and security:** This is a local-development prototype. Do not publish the dev ports to the public internet. The game engine controls clue unlocks and critical contradictions, but AI text can still hallucinate or spoil something. Before a public release, add content validation, authentication, rate limits, and secure deployment.

## Faster, in-character local AI (v0.3)

The dialogue adapter requests Ollama's native `/api/chat` endpoint with `think: false`, `keep_alive: 30m`, `num_predict: 75`, and `num_ctx: 2048`. It sends `/no_think` for Qwen3, ignores the `message.thinking` field, rejects obvious planning text, and uses the scripted fallback when the reply cannot be safely displayed. This is a best-effort guard, not a guarantee against all accidental reveals. Dialogue generation does not change case rules.

After changing backend files, rebuild: `docker compose up --build -d`, then open http://localhost:5173. To inspect backend errors: `docker compose logs -f backend`. To check whether Ollama is running on GPU: `ollama ps` in Windows terminal.
