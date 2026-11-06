import os
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app, CHARACTERS, fresh_state, evolve_character, unlocked_reveals, load

client = TestClient(app)


def headers():
    return {'X-Session-Id': str(uuid4())}


def test_every_character_has_distinct_traits_and_state():
    state = fresh_state()
    assert set(state['character_states']) == set(CHARACTERS)
    voices = {cfg['voice'] for cfg in CHARACTERS.values()}
    assert len(voices) == 3
    assert state['character_states']['alex']['trust'] != state['character_states']['leon']['trust']


def test_accusation_changes_state_without_unlocking_evidence():
    state = fresh_state()
    initial = dict(state['character_states']['alex'])
    updated = evolve_character('alex', 'You are lying!', None, state)
    assert updated['pressure'] > initial['pressure']
    assert updated['trust'] < initial['trust']
    assert updated['revealed'] == []
    assert unlocked_reveals('alex', state) == []


def test_only_presented_collected_evidence_unlocks_character_fact():
    state = fresh_state()
    state['collected'] = ['e02']
    evolve_character('alex', 'Where were you?', None, state)
    assert unlocked_reveals('alex', state) == []
    evolve_character('alex', 'Explain this log', 'e02', state)
    assert [r['id'] for r in unlocked_reveals('alex', state)] == ['late_return']


def test_character_state_survives_tab_refresh_and_reset():
    h = headers()
    initial = client.get('/api/state', headers=h).json()
    assert initial['character_states']['leon']['interactions'] == 0
    reply = client.post('/api/interrogate', headers=h, json={
        'character_id':'leon', 'question':'You are lying!'
    })
    assert reply.status_code == 200
    after = client.get('/api/state', headers=h).json()
    assert after['character_states']['leon']['interactions'] == 1
    assert after['character_states']['leon']['pressure'] > initial['character_states']['leon']['pressure']
    assert len(after['interviews']) == 1
    reset = client.post('/api/reset', headers=h).json()
    assert reset['character_states']['leon']['interactions'] == 0
    assert reset['interviews'] == []


def test_old_sessions_migrate_lazily():
    from app.main import ensure_character_states
    old = {'collected': [], 'solved': [], 'interviews': [{'character':'alex','question':'hi','reply':'hello'}], 'events':[], 'finished':False,'result':None}
    migrated = ensure_character_states(old)
    assert len(migrated['interviews']) == 1
    assert set(migrated['character_states']) == {'alex','dana','leon'}
