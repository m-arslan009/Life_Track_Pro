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

    elif intent_type == "UPDATE_PROJECT":
        payload = {
            "project_id": fields.get("project_id"),
            "updates": {k: v for k, v in fields.items() if k != "project_id"}
        }
        return {"operation": "UPDATE_PROJECT", "payload": payload}

    elif intent_type == "UPDATE_TASK":
        payload = {
            "task_id": fields.get("task_id"),
            "updates": {k: v for k, v in fields.items() if k != "task_id"}
        }
        return {"operation": "UPDATE_TASK", "payload": payload}

    elif intent_type == "CREATE_MILESTONE":
        payload = {
            "title": fields.get("title", ""),
            "description": fields.get("description", ""),
            "project_id": fields.get("project_id"),
            "start_date": fields.get("start_date"),
            "due_date": fields.get("due_date"),
        }
        return {"operation": "CREATE_MILESTONE", "payload": payload}

    elif intent_type == "UPDATE_MILESTONE":
        payload = {
            "milestone_id": fields.get("milestone_id"),
            "project_id": fields.get("project_id"),
            "updates": {k: v for k, v in fields.items() if k not in ["milestone_id", "project_id"]}
        }
        return {"operation": "UPDATE_MILESTONE", "payload": payload}

    elif intent_type == "ADD_MEMBER":
        payload = {
            "project_id": fields.get("project_id"),
            "user_id": fields.get("user_id"),
            "role": fields.get("role", "developer"),
        }
        return {"operation": "ADD_MEMBER", "payload": payload}

    elif intent_type == "READ":
        payload = {
            "query_type": fields.get("query_type", "")
        }
        return {"operation": "READ", "payload": payload}

    elif intent_type == "DELETE":
        delete_type = fields.get("delete_type", "")
        payload = {"delete_type": delete_type}
        if fields.get("delete_all"):
            payload["delete_all"] = True
        if fields.get("project_id"):
            payload["project_id"] = fields.get("project_id")
        if fields.get("task_id"):
            payload["task_id"] = fields.get("task_id")
        return {"operation": "DELETE", "payload": payload}

    elif intent_type == "READ_NOTIFICATIONS":
        return {"operation": "READ", "payload": {"query_type": "notifications"}}

    elif intent_type == "READ_PROJECT_MEMBERS":
        return {"operation": "READ", "payload": {"query_type": "project_members", "project_id": fields.get("project_id")}}

    elif intent_type == "READ_PROJECT_MILESTONES":
        return {"operation": "READ", "payload": {"query_type": "project_milestones", "project_id": fields.get("project_id")}}

    elif intent_type == "READ_MILESTONE_TASKS":
        return {"operation": "READ", "payload": {"query_type": "milestone_tasks", "milestone_id": fields.get("milestone_id"), "project_id": fields.get("project_id")}}

    elif intent_type == "READ_MEMBER_TASKS":
        return {"operation": "READ", "payload": {"query_type": "member_tasks", "member_id": fields.get("member_id")}}

    elif intent_type == "REMOVE_MEMBER":
        return {"operation": "REMOVE_MEMBER", "payload": {"project_id": fields.get("project_id"), "member_id": fields.get("member_id")}}

    elif intent_type == "UPDATE_MEMBER_ROLE":
        return {"operation": "UPDATE_MEMBER_ROLE", "payload": {"project_id": fields.get("project_id"), "member_id": fields.get("member_id"), "role": fields.get("role", "developer")}}

    elif intent_type == "DELETE_MILESTONE":
        payload = {"milestone_id": fields.get("milestone_id")}
        if fields.get("project_id"):
            payload["project_id"] = fields.get("project_id")
        return {"operation": "DELETE_MILESTONE", "payload": payload}

    elif intent_type == "DELETE_TASKS_BY_PROJECT":
        return {"operation": "DELETE_TASKS_BY_PROJECT", "payload": {"project_id": fields.get("project_id")}}

    elif intent_type == "DELETE_TASKS_BY_MILESTONE":
        return {"operation": "DELETE_TASKS_BY_MILESTONE", "payload": {"milestone_id": fields.get("milestone_id"), "project_id": fields.get("project_id")}}

    elif intent_type == "SHOW_MEMBERS":
        return {"operation": "SHOW_MEMBERS", "payload": {"project_id": fields.get("project_id"), "member_filter": fields.get("member_filter", "")}}

    else:
        return {"operation": "UNKNOWN", "payload": {}}
