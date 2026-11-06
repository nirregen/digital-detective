"""Digital Detective MVP: deterministic game rules, scripted dialogue adapter.

No LLM calls yet. The server is the sole authority for clues, gates, and endings.
"""
import json
import os
import re
import sqlite3
from pathlib import Path
from threading import Lock
from typing import Literal
from uuid import UUID

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
CASE = json.loads((ROOT / 'cases' / 'case_001.json').read_text(encoding='utf-8'))
DB_PATH = Path(os.environ.get('DD_DB_PATH', str(ROOT / 'backend' / 'detective.db')))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LOCK = Lock()
app = FastAPI(title='Digital Detective API', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=os.getenv('DD_CORS_ORIGINS', 'http://localhost:5173').split(','), allow_credentials=False, allow_methods=['GET','POST'], allow_headers=['*'])


def fresh_state():
    return {"collected": [], "solved": [], "interviews": [], "finished": False, "result": None, "events": []}


def connection():
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, state_json TEXT NOT NULL)')
    return db


def load(session_id: str):
    with connection() as db:
        row = db.execute('SELECT state_json FROM sessions WHERE session_id=?', (session_id,)).fetchone()
    return json.loads(row[0]) if row else fresh_state()


def save(session_id: str, state: dict):
    with connection() as db:
        db.execute('INSERT OR REPLACE INTO sessions VALUES (?, ?)', (session_id, json.dumps(state)))


def session_id(x_session_id: str = Header(...)) -> str:
    try:
        return str(UUID(x_session_id))
    except ValueError as exc:
        raise HTTPException(400, 'X-Session-Id must be a UUID') from exc


def public_state(state: dict):
    return {**state, "available": [e['id'] for e in CASE['evidence'] if allowed(e, state)]}


def allowed(e: dict, state: dict) -> bool:
    return all(g in state['solved'] for g in e.get('requires', [])) and all(x in state['collected'] for x in e.get('needs_evidence', []))


class PuzzleAnswer(BaseModel):
    answer: str = Field(min_length=1, max_length=200)


class TimelineAnswer(BaseModel):
    order: list[str] = Field(min_length=4, max_length=4)


class InterviewRequest(BaseModel):
    character_id: Literal['alex','dana','leon']
    question: str = Field(min_length=1, max_length=500)
    presented_evidence: str | None = None


class VerdictRequest(BaseModel):
    responsible: Literal['alex','dana','leon']
    evidence_ids: list[str] = Field(min_length=1, max_length=8)


@app.get('/api/health')
def health():
    return {"status": "ok"}


@app.get('/api/case')
def case(x_session_id: str = Header(...)):
    # Never expose locked evidence text or the canonical solution to the browser.
    current = load(session_id(x_session_id))
    visible_evidence = [e if allowed(e, current) else {**e, "title": "ENCRYPTED FILE", "content": ""} for e in CASE["evidence"]]
    return {
        "id": CASE['id'], "title": CASE['title'], "tagline": CASE['tagline'],
        "intro": CASE['intro'], "characters": CASE['characters'],
        "evidence": visible_evidence,
        "puzzles": {
            "decrypt": {k:v for k,v in CASE['puzzles']['decrypt'].items() if k != 'answer'},
            "timeline": {k:v for k,v in CASE['puzzles']['timeline'].items() if k != 'answer'},
        },
    }


@app.get('/api/state')
def state(x_session_id: str = Header(...)):
    return public_state(load(session_id(x_session_id)))


@app.post('/api/evidence/{evidence_id}/collect')
def collect(evidence_id: str, x_session_id: str = Header(...)):
    sid = session_id(x_session_id)
    e = next((x for x in CASE['evidence'] if x['id'] == evidence_id), None)
    if not e:
        raise HTTPException(404, 'Unknown evidence')
    with LOCK:
        s = load(sid)
        if not allowed(e, s):
            raise HTTPException(403, 'Evidence not unlocked')
        if evidence_id not in s['collected']:
            s['collected'].append(evidence_id)
            s['events'].append({'type':'evidence_collected','id':evidence_id})
            save(sid, s)
    return public_state(s)


@app.post('/api/puzzles/decrypt')
def decrypt(payload: PuzzleAnswer, x_session_id: str = Header(...)):
    sid = session_id(x_session_id)
    correct = re.sub(r'[^A-Z]', '', payload.answer.upper()) == re.sub(r'[^A-Z]', '', CASE['puzzles']['decrypt']['answer'])
    with LOCK:
        s = load(sid)
        if 'e04' not in s['collected']:
            raise HTTPException(403, 'Find the desk note first')
        if correct and 'decrypt' not in s['solved']:
            s['solved'].append('decrypt')
            s['events'].append({'type':'puzzle_solved','id':'decrypt'})
            save(sid, s)
    return {"correct": correct, "state": public_state(s)}


@app.post('/api/puzzles/timeline')
def timeline(payload: TimelineAnswer, x_session_id: str = Header(...)):
    sid = session_id(x_session_id)
    with LOCK:
        s = load(sid)
        if not all(e in s['collected'] for e in ['e01','e02','e03','e06']):
            raise HTTPException(403, 'Collect the email, access log, camera still and audit diff')
        correct = payload.order == CASE['puzzles']['timeline']['answer']
        if correct and 'timeline' not in s['solved']:
            s['solved'].append('timeline')
            s['events'].append({'type':'puzzle_solved','id':'timeline'})
            save(sid, s)
    return {"correct": correct, "state": public_state(s)}


@app.post('/api/interrogate')
def interrogate(payload: InterviewRequest, x_session_id: str = Header(...)):
    sid = session_id(x_session_id)
    q = payload.question.lower()
    with LOCK:
        s = load(sid)
        if payload.presented_evidence and payload.presented_evidence not in s['collected']:
            raise HTTPException(403, 'You cannot present evidence you have not collected')
        contradiction = payload.character_id == 'alex' and payload.presented_evidence == 'e02'
        if contradiction:
            reply = "You're right. I came back at 22:14. I helped copy a backup, but I can't tell you who asked me until you establish what was altered."
        elif payload.character_id == 'alex':
            reply = "I left at 20:00. That's what my statement says. What exactly do you want to know?"
        elif payload.character_id == 'dana':
            reply = "Maya had concerns about audit changes. Look at the documents before trusting anyone's timeline."
        elif 'e06' in s['collected'] and payload.presented_evidence == 'e06':
            reply = "A privileged account doesn't prove who typed the commands. I won't discuss internal controls with you."
        else:
            reply = "The resignation is official. I have nothing further to add."
        # Scripted adapter: question is recorded but never executed or used as a system instruction.
        s['interviews'].append({'character':payload.character_id, 'question':payload.question, 'evidence':payload.presented_evidence, 'reply':reply})
        s['events'].append({'type':'interview','id':payload.character_id, 'contradiction':contradiction})
        save(sid, s)
    return {"reply":reply, "contradiction":contradiction, "state":public_state(s)}


@app.post('/api/submit')
def submit(payload: VerdictRequest, x_session_id: str = Header(...)):
    sid = session_id(x_session_id)
    with LOCK:
        s = load(sid)
        if not all(e in s['collected'] for e in ['e02','e06','e08']):
            raise HTTPException(403, 'Investigate further before submitting your verdict')
        if not set(payload.evidence_ids).issubset(set(s['collected'])):
            raise HTTPException(403, 'Verdict uses uncollected evidence')
        correct = payload.responsible == CASE['solution']['responsible'] and set(CASE['solution']['required_evidence']).issubset(payload.evidence_ids)
        s['finished'] = correct
        s['result'] = 'solved' if correct else 'incorrect'
        s['events'].append({'type':'verdict','correct':correct})
        save(sid,s)
    return {"correct":correct, "message":CASE['solution']['summary'] if correct else 'The evidence does not support that conclusion. Review the audit trail and Maya’s note.', "state":public_state(s)}


@app.post('/api/reset')
def reset(x_session_id: str = Header(...)):
    sid = session_id(x_session_id)
    s = fresh_state()
    with LOCK:
        save(sid, s)
    return public_state(s)
