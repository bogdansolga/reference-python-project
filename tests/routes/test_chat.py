# tests/routes/test_chat.py
import pytest
from flask import Flask

import routes.chat as chat


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(chat.bp)
    return app.test_client()


class _FakeStream:
    """Mimics the context manager returned by client.messages.stream(...)."""

    def __init__(self, chunks):
        self._chunks = chunks

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    @property
    def text_stream(self):
        yield from self._chunks


class _FakeMessages:
    def __init__(self, chunks, recorder):
        self._chunks = chunks
        self._recorder = recorder

    def stream(self, **kwargs):
        self._recorder.update(kwargs)
        return _FakeStream(self._chunks)


class _FakeClient:
    def __init__(self, chunks, recorder):
        self.messages = _FakeMessages(chunks, recorder)


def test_resolve_model_defaults_to_sonnet(monkeypatch):
    monkeypatch.delenv("CHAT_MODEL", raising=False)
    assert chat._resolve_model() == "claude-sonnet-4-6"


def test_resolve_model_honors_env(monkeypatch):
    monkeypatch.setenv("CHAT_MODEL", "claude-sonnet-4-6")
    assert chat._resolve_model() == "claude-sonnet-4-6"


def test_use_vertex_true_when_project_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_VERTEX_PROJECT_ID", "my-gcp-project")
    assert chat._use_vertex() is True


def test_use_vertex_false_when_project_absent(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_VERTEX_PROJECT_ID", raising=False)
    assert chat._use_vertex() is False


def test_chat_requires_messages(client):
    resp = client.post("/api/chat", json={"messages": []})
    assert resp.status_code == 400


def test_chat_direct_backend_without_key_returns_500(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_VERTEX_PROJECT_ID", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    resp = client.post("/api/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    assert resp.status_code == 500


def test_chat_streams_text_and_passes_system_separately(client, monkeypatch):
    recorder = {}
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.delenv("ANTHROPIC_VERTEX_PROJECT_ID", raising=False)
    monkeypatch.setattr(
        chat, "_build_client", lambda: _FakeClient(["Hello", " ", "world"], recorder)
    )

    user_messages = [{"role": "user", "content": "Say hello"}]
    resp = client.post("/api/chat", json={"messages": user_messages})

    assert resp.status_code == 200
    assert resp.mimetype == "text/plain"
    assert resp.get_data(as_text=True) == "Hello world"

    # System prompt goes via the top-level `system=` param, NOT in messages.
    assert recorder["system"] == chat.SYSTEM_PROMPT
    assert recorder["messages"] == user_messages
    assert "max_tokens" in recorder
    assert recorder["model"] == "claude-sonnet-4-6"
