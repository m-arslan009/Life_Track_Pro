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


def _format_success_response(result):
    """Format successful READ operation results into readable text."""
    if not result.get("success"):
        return None
    
    output = ""
    if "projects" in result:
        projects = result["projects"]
        output = "Projects ({} found):\n".format(len(projects))
        for p in projects:
            output += "- {} (ID: {}, Status: {})\n".format(p.get("name", "N/A"), p.get("id", "N/A"), p.get("status", "N/A"))
    
    elif "tasks" in result:
        tasks = result["tasks"]
        output = "Tasks ({} found):\n".format(len(tasks))
        for t in tasks:
            output += "- {} (ID: {}, Status: {})\n".format(t.get("title", "N/A"), t.get("id", "N/A"), t.get("status", "N/A"))
    
    elif "milestones" in result:
        milestones = result["milestones"]
        output = "Milestones ({} found):\n".format(len(milestones))
        for m in milestones:
            output += "- {} (ID: {}, Status: {})\n".format(m.get("title", "N/A"), m.get("id", "N/A"), m.get("status", "N/A"))
    
    elif "notifications" in result:
        notifications = result["notifications"]
        output = "Notifications ({} found):\n".format(len(notifications))
        for n in notifications:
            output += "- {}\n".format(n.get("message", "N/A"))
    
    elif "members" in result:
        members = result["members"]
        output = "Members ({} found):\n".format(len(members))
        for m in members:
            output += "- {} (Role: {}, Availability: {})\n".format(m.get("username", "N/A"), m.get("role", "N/A"), m.get("availability", "N/A"))
    
    else:
        return None
    
    return output.strip()


def success(result):
    # Try to format as structured data first for READ operations
    formatted = _format_success_response(result)
    if formatted:
        return formatted
    
    # Otherwise use LLM for generic success message
    result_str = json.dumps(result) if isinstance(result, dict) else str(result)
    prompt = f"Generate a friendly, positive, concise success message for this operation result: {result_str}. No extra text."
    return call_llm(prompt, mode="explanation")
