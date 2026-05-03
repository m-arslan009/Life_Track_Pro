"""Formats orchestration outputs into user-facing responses using LLM."""
import json
from .services.llm_router import call_llm


def ask_for_missing(state):
    missing_fields = state.get("missing_fields", [])
    if not missing_fields:
        return "All required fields are provided."
    prompt = f"Generate a friendly, concise message asking the user to provide the following missing fields: {', '.join(missing_fields)}. Be polite and clear, no extra text."
    return call_llm(prompt, mode="explanation")


def explain_error(error):
    prompt = f"Rewrite the following error message into a friendly, easy-to-understand message for the user: {error}. Keep it concise, no extra text."
    return call_llm(prompt, mode="explanation")


def success(result):
    result_str = json.dumps(result) if isinstance(result, dict) else str(result)
    prompt = f"Generate a friendly, positive, concise success message for this operation result: {result_str}. No extra text."
    return call_llm(prompt, mode="explanation")
