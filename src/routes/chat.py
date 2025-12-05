import os
from flask import Blueprint, request, Response, jsonify
from openai import OpenAI
from lib.constants import HTTP_BAD_REQUEST

bp = Blueprint("chat", __name__, url_prefix="/api/chat")

SYSTEM_PROMPT = """You are a helpful assistant for a product management system.
You can help users understand and manage their products and sections."""


@bp.route("", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", []) if data else []

    if not messages:
        return jsonify({"error": "Messages required"}), HTTP_BAD_REQUEST

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return jsonify({"error": "OpenAI API key not configured"}), HTTP_BAD_REQUEST

    client = OpenAI(api_key=api_key)

    def generate():
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return Response(generate(), mimetype="text/plain")
