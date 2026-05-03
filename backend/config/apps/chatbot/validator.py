"""Validates parsed intents and generated query schemas."""
from typing import Dict, Any, List


REQUIRED_FIELDS = {
    "CREATE_PROJECT": ["project_name", "start_date", "due_date"],
    "CREATE_TASK": ["title", "project_id"],
    "CREATE_MILESTONE": ["title", "project_id", "start_date", "due_date"],
    "UPDATE_PROJECT": ["project_id"],
    "UPDATE_TASK": ["task_id"],
    "UPDATE_MILESTONE": ["milestone_id"],
    "ADD_MEMBER": ["project_id", "user_id"],
    "REMOVE_MEMBER": ["project_id", "member_id"],
    "UPDATE_MEMBER_ROLE": ["project_id", "member_id"],
    "DELETE_MILESTONE": ["milestone_id"],
    "DELETE_TASKS_BY_PROJECT": ["project_id"],
    "DELETE_TASKS_BY_MILESTONE": ["milestone_id", "project_id"],
    "SHOW_MEMBERS": ["project_id"],
    "READ": ["query_type"],
}


def validate(planned_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a planned schema from schema_planner.

    Args:
        planned_schema: Output from schema_planner.plan_schema()
                      Contains 'operation' and 'payload' keys

    Returns:
        Dict with 'ok' (bool) and 'error' (str or None) keys
    """
    operation = planned_schema.get("operation")
    payload = planned_schema.get("payload", {})

    if operation == "UNKNOWN":
        return {"ok": False, "error": "Unknown intent, cannot process request"}

    required_fields = REQUIRED_FIELDS.get(operation, [])
    missing_fields = [field for field in required_fields if not payload.get(field)]

    if missing_fields:
        return {
            "ok": False,
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }

    return {"ok": True, "error": None}
