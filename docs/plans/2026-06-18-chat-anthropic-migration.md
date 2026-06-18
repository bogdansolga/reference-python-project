# Migration plan — `/api/chat` from OpenAI to Anthropic

**Goal:** make `reference-python-project`'s chat feature mirror `reference-c-sharp-project/web/src/app/api/chat/route.ts` in **behavior and API usage**, on the official Anthropic Python SDK — with a dual backend so it runs both for trainer demos (direct API key) and on the ING/GCP path (Claude on Vertex AI), with no API key on the client's laptop.

## Scope

In scope: `src/routes/chat.py`, `pyproject.toml`, `.env.example`, `README.md` (chat/env sections), new tests.

Out of scope: the sections/products/auth REST layers. They are already a parallel port of the same reference (routes→services→repositories→schemas + `lib/errors` + app-level error handlers), so their behavior already matches the C# `Endpoints/Services/Repositories/Dtos/Validation/Http` layering. Churning them would risk the green test suite for no parity gain.

## Reference behavior (from the C# route)

- System prompt read from `src/prompts/chat-system.md` (Python already does this; prompt content is identical bar the curl port).
- Default model `claude-haiku-4-5`, overridable via `CHAT_MODEL`.
- Streaming response.
- Requires credentials; missing key → 500.

## Target design

`src/routes/chat.py`:
- **Anthropic SDK**, not OpenAI. System prompt goes in the top-level `system=` parameter (Anthropic), **not** prepended as a `system` message (that was the OpenAI shape).
- **Model:** `CHAT_MODEL` env override; default `claude-haiku-4-5`. On Vertex the operator must set `CHAT_MODEL` to the Vertex-formatted id (`claude-haiku-4-5@<date>`) — IDs differ on Vertex.
- **Dual backend** (`_build_client()`):
  - Vertex when `ANTHROPIC_VERTEX_PROJECT_ID` is set (region from `CLOUD_ML_REGION`/`ANTHROPIC_VERTEX_REGION`): `AnthropicVertex(region=..., project_id=...)` — auth via gcloud ADC, no key. This is the ING/GCP path.
  - Direct otherwise: `Anthropic(api_key=ANTHROPIC_API_KEY)`. Trainer demo path.
- **`max_tokens`** required by Anthropic — default 1024, override `CHAT_MAX_TOKENS`.
- **Streaming:** `with client.messages.stream(model=, max_tokens=, system=SYSTEM_PROMPT, messages=messages) as stream: yield from stream.text_stream`. Response stays `mimetype="text/plain"` — the existing contract; no frontend consumes a special protocol (the Jinja template only lists the endpoint).
- **Error handling:** no messages → 400 (keep); direct backend with no `ANTHROPIC_API_KEY` → 500 (mirror C#).

Testable seams (no network in tests): `_resolve_model()`, `_use_vertex()`, `_build_client()` (monkeypatched in tests), `_stream_text(client, messages)`.

## Tests first (TDD)

`tests/routes/test_chat.py` (new), against the Flask test client with a fake client injected via monkeypatching `chat._build_client`:
1. `_resolve_model()` → `claude-haiku-4-5` by default; honors `CHAT_MODEL`.
2. `_use_vertex()` → True iff `ANTHROPIC_VERTEX_PROJECT_ID` set.
3. POST `/api/chat` with no messages → 400.
4. POST `/api/chat`, direct backend, no `ANTHROPIC_API_KEY` → 500.
5. POST `/api/chat`, happy path with fake streaming client → 200, `text/plain`, body = concatenated `text_stream`, and the fake received `system=` + the user messages (system not in messages array).

## Dependency + config changes

- `pyproject.toml`: drop `openai>=1.0`; add `anthropic[vertex]>=0.40`.
- `.env.example`: replace `OPENAI_API_KEY` with `ANTHROPIC_API_KEY`, `# CHAT_MODEL=claude-haiku-4-5`, and commented Vertex vars (`ANTHROPIC_VERTEX_PROJECT_ID`, `CLOUD_ML_REGION`).
- `README.md`: chat section notes the AI runs via Anthropic (direct key) or Claude-on-Vertex (GCP) — not OpenAI.

## Verify

`pytest` green (existing suite + new chat tests).
