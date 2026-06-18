import os
from pathlib import Path
from flask import Blueprint, request, Response, jsonify
from lib.constants import HTTP_BAD_REQUEST, HTTP_INTERNAL_ERROR

bp = Blueprint("chat", __name__, url_prefix="/api/chat")

# Load system prompt from file
_prompt_path = Path(__file__).parent.parent / "prompts" / "chat-system.md"
SYSTEM_PROMPT = _prompt_path.read_text()

# Claude by default (the AI part of the course runs on Claude — via a direct
# Anthropic key for trainer demos, or Claude on Vertex AI for the GCP path).
# Override with CHAT_MODEL. On Vertex, model ids are date-suffixed
# (e.g. "claude-haiku-4-5@20251001") — set CHAT_MODEL accordingly.
DEFAULT_MODEL = "claude-haiku-4-5"
DEFAULT_MAX_TOKENS = 1024


def _resolve_model() -> str:
    return os.environ.get("CHAT_MODEL", DEFAULT_MODEL)


def _resolve_max_tokens() -> int:
    return int(os.environ.get("CHAT_MAX_TOKENS", str(DEFAULT_MAX_TOKENS)))


def _use_vertex() -> bool:
    """Use Claude on Vertex AI when a GCP project is configured.

    This is the ING/GCP path: auth comes from gcloud Application Default
    Credentials, so no API key ever lives on the client's laptop.
    """
    return bool(os.environ.get("ANTHROPIC_VERTEX_PROJECT_ID"))


def _build_client():
    """Build the Anthropic client for the configured backend.

    - Vertex: AnthropicVertex(region, project_id) — credentials via gcloud ADC.
    - Direct: Anthropic(api_key=...) — trainer demo path.
    """
    if _use_vertex():
        from anthropic import AnthropicVertex

        return AnthropicVertex(
            project_id=os.environ["ANTHROPIC_VERTEX_PROJECT_ID"],
            region=os.environ.get("CLOUD_ML_REGION")
            or os.environ.get("ANTHROPIC_VERTEX_REGION", "us-east5"),
        )

    from anthropic import Anthropic

    return Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


@bp.route("", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", []) if data else []

    if not messages:
        return jsonify({"error": "Messages required"}), HTTP_BAD_REQUEST

    # Direct backend needs an API key; the Vertex backend authenticates via
    # gcloud ADC instead. Mirror the C# reference: missing config -> 500.
    if not _use_vertex() and not os.environ.get("ANTHROPIC_API_KEY"):
        return (
            jsonify({"error": "The ANTHROPIC_API_KEY environment variable is not configured"}),
            HTTP_INTERNAL_ERROR,
        )

    client = _build_client()
    model = _resolve_model()
    max_tokens = _resolve_max_tokens()

    def generate():
        # System prompt is a top-level Anthropic parameter — not a message.
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text

    return Response(generate(), mimetype="text/plain")
