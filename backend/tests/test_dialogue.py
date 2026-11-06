from app.main import clean_character_reply
import pytest

def test_strips_thinking_blocks():
    assert clean_character_reply('<think>Let me plan this.</think> I left at eight.', 'alex', None) == 'I left at eight.'

def test_rejects_visible_thoughts():
    with pytest.raises(ValueError):
        clean_character_reply('Hmm, the user is asking where I was. I should avoid details.', 'alex', None)

def test_rejects_early_spoiler():
    with pytest.raises(ValueError):
        clean_character_reply('I returned at 22:14.', 'alex', None)

def test_accepts_natural_dialogue():
    assert clean_character_reply('Alex Morgan: I left at eight. Ask the guard.', 'alex', None) == 'I left at eight. Ask the guard.'
