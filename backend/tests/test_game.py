import os
import tempfile
from uuid import uuid4

# Configure before import so test sessions are isolated from normal development data.
os.environ['DD_DB_PATH'] = os.path.join(tempfile.gettempdir(), f'dd_tests_{uuid4().hex}.db')
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def session():
    return {'X-Session-Id':str(uuid4())}

def collect(h, e):
    return client.post(f'/api/evidence/{e}/collect',headers=h)

def setup_to_timeline(h):
    for e in ['e01','e03','e04','e07']:
        assert collect(h,e).status_code == 200
    assert client.post('/api/puzzles/decrypt',headers=h,json={'answer':'check the backup'}).json()['correct']
    for e in ['e02','e05','e06']:
        assert collect(h,e).status_code == 200


def test_locked_evidence_and_no_answers_leak():
    h=session()
    assert collect(h,'e02').status_code == 403
    body=client.get('/api/case', headers=h).json()
    assert 'solution' not in body
    assert 'answer' not in body['puzzles']['timeline']
    assert next(e for e in body['evidence'] if e['id']=='e06')['content'] == ''


def test_game_happy_path():
    h=session()
    setup_to_timeline(h)
    response=client.post('/api/interrogate',headers=h,json={'character_id':'alex','question':'Why were you inside?','presented_evidence':'e02'})
    assert response.json()['contradiction'] is True
    wrong=client.post('/api/puzzles/timeline',headers=h,json={'order':['email','audit','camera','badge']})
    assert not wrong.json()['correct']
    correct=client.post('/api/puzzles/timeline',headers=h,json={'order':['audit','email','camera','badge']})
    assert correct.json()['correct']
    assert collect(h,'e08').status_code == 200
    verdict=client.post('/api/submit',headers=h,json={'responsible':'leon','evidence_ids':['e02','e06','e08']})
    assert verdict.json()['correct'] is True


def test_cannot_present_unfound_evidence():
    h=session()
    response=client.post('/api/interrogate',headers=h,json={'character_id':'alex','question':'You lied','presented_evidence':'e02'})
    assert response.status_code == 403


def test_bad_session_rejected():
    assert client.get('/api/state',headers={'X-Session-Id':'bad'}).status_code == 400
