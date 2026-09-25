"""Tests for the Digital Twin app. Run with: python -m pytest"""
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest

from utils.rag import entry_to_text, load_knowledge_base, parse_upload, retrieve
from utils.tools import calculate, get_current_time

KNOWLEDGE_BASE = ROOT / "data" / "knowledge_base.json"


# ---------- tools.py ----------

def test_calculate_basic_maths():
    assert calculate("2 + 3 * 4") == "14"
    assert calculate("(12 + 4) * 2") == "32"
    assert calculate("-5 + 10") == "5"


def test_calculate_division_by_zero():
    assert calculate("1 / 0").startswith("Error")


def test_calculate_rejects_code():
    assert calculate("__import__('os').system('ls')").startswith("Error")


def test_get_current_time_has_year():
    assert str(__import__("datetime").datetime.now().year) in get_current_time()


# ---------- rag.py ----------

def test_knowledge_base_loads():
    entries = load_knowledge_base(KNOWLEDGE_BASE)
    assert len(entries) > 0
    assert all({"day", "time", "text"} <= entry.keys() for entry in entries)


def test_missing_knowledge_base_returns_empty():
    assert load_knowledge_base(ROOT / "data" / "does_not_exist.json") == []


def test_retrieve_finds_breakfast():
    entries = load_knowledge_base(KNOWLEDGE_BASE)
    results = retrieve("What did I eat for breakfast on Monday?", entries)
    assert results
    assert "scrambled eggs" in results[0]


def test_retrieve_returns_nothing_for_unrelated_question():
    entries = load_knowledge_base(KNOWLEDGE_BASE)
    assert retrieve("quantum physics", entries) == []


def test_entry_to_text():
    entry = {"day": "Monday", "time": "7:45am", "text": "Had eggs."}
    assert entry_to_text(entry) == "Monday 7:45am - Had eggs."


def test_parse_upload_txt():
    entries = parse_upload("notes.txt", b"First note.\n\nSecond note.")
    assert [e["text"] for e in entries] == ["First note.", "Second note."]


def test_parse_upload_json():
    content = b'{"entries": [{"day": "Friday", "time": "9am", "text": "Gym."}]}'
    assert parse_upload("more.json", content)[0]["text"] == "Gym."


# ---------- app.py ----------

def fake_gemini(reply="Hello from the twin!"):
    fake = mock.MagicMock()
    response = fake.return_value.models.generate_content.return_value
    response.text = reply
    response.automatic_function_calling_history = []
    return fake


def test_app_loads():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    at.secrets["GEMINI_API_KEY"] = "test-key"
    at.run()
    assert not at.exception
    assert at.title[0].value == "🤖 Digital Twin Assistant"


def test_chat_reply_with_sources():
    fake = fake_gemini("You had scrambled eggs and toast.")
    with mock.patch("google.genai.Client", fake):
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        at.secrets["GEMINI_API_KEY"] = "test-key"
        at.run()
        at.chat_input[0].set_value("What did I eat for breakfast on Monday?").run()

    assert not at.exception
    last = at.session_state.messages[-1]
    assert last["content"] == "You had scrambled eggs and toast."
    assert any("scrambled eggs" in s for s in last["sources"])


def test_clear_chat():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    at.secrets["GEMINI_API_KEY"] = "test-key"
    at.run()
    at.sidebar.button[0].click().run()
    assert len(at.session_state.messages) == 0
