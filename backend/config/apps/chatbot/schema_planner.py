"""Generates abstract operation plans based on parsed user intents."""
from typing import Dict, Any


def plan_schema(parsed_intent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps a parsed intent and collected fields to an abstract operation.

    Args:
        parsed_intent: Output from intent_parser.parse_intent()
                      Contains 'intent', 'fields', and 'confidence' keys

    Returns:
        Dict with 'operation' and 'payload' keys
    """
    intent_type = parsed_intent.get("intent", "UNKNOWN")
    fields = parsed_intent.get("fields", {})

    if intent_type == "CREATE_PROJECT":
        payload = {
            "project_name": fields.get("project_name", ""),
            "project_description": fields.get("project_description", ""),
            "due_date": fields.get("due_date"),
            "start_date": fields.get("start_date"),
            "status": fields.get("status", "active"),
            "progress": fields.get("progress", 0),
        }
        # Remove None values so Django uses model defaults or allows null
        payload = {k: v for k, v in payload.items() if v is not None}
        return {"operation": "CREATE_PROJECT", "payload": payload}

    elif intent_type == "CREATE_TASK":
        payload = {
            "title": fields.get("title", ""),
            "description": fields.get("description", ""),
            "project_id": fields.get("project_id"),
            "milestone_id": fields.get("milestone_id"),
            "assignee_id": fields.get("assignee_id"),
            "status": fields.get("status", "todo"),
        }
        return {"operation": "CREATE_TASK", "payload": payload}

    elif intent_type == "UPDATE_TASK":
        payload = {
            "task_id": fields.get("task_id"),
            "updates": {k: v for k, v in fields.items() if k != "task_id"}
        }
        return {"operation": "UPDATE_TASK", "payload": payload}

    elif intent_type == "READ":
        payload = {
            "query_type": fields.get("query_type", "")
        }
        return {"operation": "READ", "payload": payload}

    else:
        return {"operation": "UNKNOWN", "payload": {}}
