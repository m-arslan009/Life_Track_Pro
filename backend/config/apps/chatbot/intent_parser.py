"""Parses user input to extract intents and entities."""
import json
from typing import Optional, Dict
from .services.llm_router import call_llm


def parse_intent(message: str, state: Optional[Dict] = None) -> Dict:
    system_prompt = """You are an intent parser for a project management chatbot. Given a user message and optional current session state, return a STRICT JSON object matching this exact schema:
{
  "intent": "CREATE_PROJECT" | "CREATE_TASK" | "UPDATE_TASK" | "READ" | "UNKNOWN",
  "fields": {},
  "confidence": 0.0
}
Rules:
- intent must be one of the specified values
- fields is an object containing extracted relevant data for the intent
- confidence is a float between 0.0 and 1.0
- For CREATE_PROJECT, use these EXACT field names: "project_name", "project_description", "start_date", "due_date"
- For CREATE_TASK, use these EXACT field names: "title", "description", "project_id", "milestone_id", "assignee_id"
- For UPDATE_TASK, use these EXACT field names: "task_id" plus any fields to update
- For READ, use field "query_type" with values like "projects", "tasks", "milestones", etc.
Return ONLY the JSON object, no markdown, no additional text."""
    user_content = f"User message: {message}"
    if state:
        user_content += f"\nCurrent session state: {json.dumps(state)}"
    full_prompt = f"{system_prompt}\n\n{user_content}"
    max_retries = 2
    for attempt in range(max_retries):
        try:
            content = call_llm(full_prompt, mode="intent")
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3].strip()
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3].strip()
            parsed = json.loads(content)
            if all(key in parsed for key in ["intent", "fields", "confidence"]):
                return parsed
            else:
                raise json.JSONDecodeError("Missing required keys", content, 0)
        except (json.JSONDecodeError, KeyError) as e:
            if attempt == max_retries - 1:
                raise ValueError(f"Failed to parse intent after {max_retries} attempts: {e}")
            continue
    raise ValueError("Failed to parse intent after retries")
