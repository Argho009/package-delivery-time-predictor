"""
routes/copilot.py — AI Logistics Copilot & Dedicated LLM API Routes
Endpoints:
  POST /api/copilot/chat           — Real-time conversational AI with shipment context
  GET  /api/copilot/status         — Local GPU & Ollama status check
  POST /api/copilot/quick-analysis — Instant executive route audit
"""

from flask import Blueprint, request, jsonify
from services.llm_service import chat_with_copilot, get_ollama_status, get_gpu_info

copilot_bp = Blueprint("copilot", __name__, url_prefix="/api/copilot")


@copilot_bp.route("/status", methods=["GET"])
def copilot_status():
    """Return local GPU acceleration and LLM server status."""
    status = get_ollama_status()
    return jsonify(status)


@copilot_bp.route("/chat", methods=["POST"])
def copilot_chat():
    """
    Handle natural-language queries from the user.
    Body JSON:
      {
        "message": "Why is this route taking 33 hours?",
        "shipment_context": { origin, destination, distance_km, recommended_hours, ... },
        "model": "llama3.2:3b",
        "history": [ { role, content }, ... ]
      }
    """
    data = request.get_json(force=True, silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Message is required."}), 400

    context = data.get("shipment_context") or {}
    model_name = data.get("model")
    history = data.get("history") or []

    result = chat_with_copilot(
        message=message,
        shipment_context=context,
        model_name=model_name,
        conversation_history=history
    )
    return jsonify(result)


@copilot_bp.route("/quick-analysis", methods=["POST"])
def quick_analysis():
    """Generate an instant 3-point executive briefing on the active shipment."""
    data = request.get_json(force=True, silent=True) or {}
    context = data.get("shipment_context") or {}
    prompt = "Provide a concise 3-bullet operational briefing for this shipment: 1) Transit assessment, 2) Route bottlenecks or weather risks, 3) Recommended action."
    result = chat_with_copilot(message=prompt, shipment_context=context)
    return jsonify(result)
