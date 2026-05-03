"""Parses user input to extract intents and entities."""
import json
from typing import Optional, Dict
from .services.llm_router import call_llm


def parse_intent(message: str, state: Optional[Dict] = None) -> Dict:
    system_prompt = """You are an intent parser for a project management chatbot. Given a user message and optional current session state, return a STRICT JSON object matching this exact schema:
{
  "intent": "CREATE_PROJECT" | "CREATE_TASK" | "CREATE_MILESTONE" | "UPDATE_PROJECT" | "UPDATE_TASK" | "UPDATE_MILESTONE" | "READ" | "DELETE" | "ADD_MEMBER" | "READ_NOTIFICATIONS" | "READ_PROJECT_MEMBERS" | "READ_PROJECT_MILESTONES" | "READ_MILESTONE_TASKS" | "READ_MEMBER_TASKS" | "REMOVE_MEMBER" | "UPDATE_MEMBER_ROLE" | "DELETE_MILESTONE" | "DELETE_TASKS_BY_PROJECT" | "DELETE_TASKS_BY_MILESTONE" | "SHOW_MEMBERS" | "UNKNOWN",
  "fields": {},
  "confidence": 0.0
}
Rules:
- intent must be one of the specified values
- fields is an object containing extracted relevant data for the intent
- confidence is a float between 0.0 and 1.0
- CRITICAL: PRESERVE EXACT CASE. If user says "abc", output "abc". If user says "ABC", output "ABC". NEVER change case.
- CRITICAL: If session state shows "missing_fields" is NOT EMPTY, the user is providing values for those missing fields. KEEP THE SAME INTENT as "last_intent" from session state. Do NOT start a new intent.
- Examples:
  - User says "delete all milestones in project abc" → "project_id": "abc" (lowercase)
  - User says "delete all milestones in project ABC" → "project_id": "ABC" (uppercase)
  - User says "show tasks in project LOPREIN" → "project_id": "LOPREIN" (exact case)
  - Session has last_intent="CREATE_PROJECT", missing_fields=["due_date"], user says "due date is 2026-11-11" → intent="CREATE_PROJECT", fields={"due_date": "2026-11-11"}
  - Session has last_intent="CREATE_PROJECT", missing_fields=["start_date"], user says "start date is 2026-08-08" → intent="CREATE_PROJECT", fields={"start_date": "2026-08-08"}
- For CREATE_PROJECT, use: "project_name", "project_description", "start_date", "due_date"
- For CREATE_TASK, use: "title", "description", "project_id", "milestone_id", "assignee_id"
- For CREATE_MILESTONE, use: "title", "description", "project_id", "start_date", "due_date"
- For UPDATE_PROJECT, use: "project_id" or "project_name" plus "due_date", "start_date", "status", "progress"
- For UPDATE_TASK, use: "task_id" plus "title", "status", "description"
- For UPDATE_MILESTONE, use: "milestone_id" plus "title", "status", "due_date"
- For READ, use "query_type" with values: "projects", "tasks", "milestones", "notifications"
- For READ_NOTIFICATIONS: no fields needed, returns user's notifications
- For READ_PROJECT_MEMBERS: use "project_id" or "project_name"
- For READ_PROJECT_MILESTONES: use "project_id" or "project_name"
- For READ_MILESTONE_TASKS: use "milestone_id" plus "project_id"
- For READ_MEMBER_TASKS: use "member_id"
- For DELETE, use "delete_type" with values: "project", "task", "milestone"; plus "project_id" or "task_id"; add "delete_all": true for ALL
- For ADD_MEMBER, use: "project_id" or "project_name", "user_id" or "username"
- For REMOVE_MEMBER: use "project_id" and "member_id"
- For UPDATE_MEMBER_ROLE: use "project_id", "member_id", "role"
- For DELETE_MILESTONE: use "milestone_id"
- For DELETE_TASKS_BY_PROJECT: use "project_id"
- For DELETE_TASKS_BY_MILESTONE: use "milestone_id" and "project_id"
- For SHOW_MEMBERS: use "project_id" and optional "member_filter" (e.g., "available")
- Examples:
  CREATE: "create project ABC", "add task XYZ to project 1"
  UPDATE: "update project ABC due date to 2026-12-31", "mark task 5 as done"
  DELETE: "delete project ABC", "remove task 3", "delete all my tasks"
  READ: "show all projects", "list tasks in project XYZ"
  ADD_MEMBER: "add user John to project ABC", "invite jane@email.com to project 1"
  SHOW_MEMBERS: "show members of project ABC", "list available members in project 1"
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
