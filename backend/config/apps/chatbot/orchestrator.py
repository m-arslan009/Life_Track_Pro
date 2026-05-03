"""Chatbot orchestration module. Coordinates intent parsing, schema planning, validation, and response generation."""
import logging
from typing import Dict, Any, Optional

from .session_store import get_session, save_session, clear_session
from .intent_parser import parse_intent
from .schema_planner import plan_schema
from .validator import validate
from .gateway_explainer import ask_for_missing, explain_error, success
from .executor import execute_operation

logger = logging.getLogger(__name__)


def handle_message(message: str, session_id: str, user=None) -> Dict[str, Any]:
    """
    Orchestrates the full chatbot message handling flow.

    Flow:
    1. Load session
    2. Parse intent (with session state context)
    3. Update state with parsed fields
    4. If missing fields → ask user via gateway_explainer
    5. Plan schema
    6. Validate
    7. Execute operation
    8. Return response (NO DB execution yet)

    Args:
        message: User's input message
        session_id: Session identifier
        user: Authenticated Django user

    Returns:
        Dict with 'response', 'missing_fields', 'errors' keys
    """
    print(f"\n[ORCHESTRATOR] Processing message: '{message}'")
    print(f"[ORCHESTRATOR] Session ID: {session_id}")
    
    # 1. Load session
    session = get_session(session_id) or {}
    print(f"[ORCHESTRATOR] Loaded session: {session if session else '{} (new session)'}")

    # 2. Parse intent
    print(f"[ORCHESTRATOR] Calling intent parser...")
    try:
        parsed = parse_intent(message, session if session else None)
        print(f"[ORCHESTRATOR] Parsed intent: {parsed}")
    except Exception as e:
        logger.error(f"Intent parsing failed: {e}")
        error_msg = str(e)
        print(f"[ORCHESTRATOR] Intent parsing FAILED: {error_msg}")
        return {
            "response": explain_error(error_msg),
            "missing_fields": [],
            "errors": [error_msg]
        }

    # 3. Update state
    state = dict(session) if session else {}
    collected = state.get("collected_fields", {})
    new_fields = parsed.get("fields", {})
    collected.update(new_fields)

    state["collected_fields"] = collected
    state["last_intent"] = parsed.get("intent")
    state["last_message"] = message
    print(f"[ORCHESTRATOR] Updated state with fields: {new_fields}")
    print(f"[ORCHESTRATOR] Total collected fields: {collected}")

    intent_type = parsed.get("intent")

    if intent_type == "UNKNOWN":
        print(f"[ORCHESTRATOR] Intent is UNKNOWN, returning default message")
        save_session(session_id, state)
        return {
            "response": "I'm not sure what you're trying to do. Could you please rephrase?",
            "missing_fields": [],
            "errors": []
        }

    # Check for missing required fields
    required = {
        "CREATE_PROJECT": ["project_name", "due_date", "start_date"],
        "CREATE_TASK": ["title", "project_id"],
        "UPDATE_TASK": ["task_id"],
        "READ": [],
    }

    required_for_intent = required.get(intent_type, [])
    missing_fields = [f for f in required_for_intent if not collected.get(f)]
    print(f"[ORCHESTRATOR] Required fields for {intent_type}: {required_for_intent}")
    print(f"[ORCHESTRATOR] Missing fields: {missing_fields}")

    # 4. If missing fields → gateway_explainer
    if missing_fields:
        print(f"[ORCHESTRATOR] Missing fields detected, calling gateway_explainer...")
        state["missing_fields"] = missing_fields
        save_session(session_id, state)
        response_text = ask_for_missing({"missing_fields": missing_fields})
        print(f"[ORCHESTRATOR] Gateway explainer response: {response_text[:200]}...")
        return {
            "response": response_text,
            "missing_fields": missing_fields,
            "errors": []
        }

    # Build complete parsed intent with all collected fields
    complete_parsed = {
        "intent": intent_type,
        "fields": collected,
        "confidence": parsed.get("confidence", 0.0)
    }

    # 5. Plan schema
    print(f"[ORCHESTRATOR] Calling schema planner with: {complete_parsed}")
    planned = plan_schema(complete_parsed)
    print(f"[ORCHESTRATOR] Planned schema: {planned}")

    # 6. Validate
    print(f"[ORCHESTRATOR] Validating planned schema...")
    validation = validate(planned)
    print(f"[ORCHESTRATOR] Validation result: {validation}")

    if not validation["ok"]:
        error_msg = validation["error"]
        state["last_error"] = error_msg
        save_session(session_id, state)
        print(f"[ORCHESTRATOR] Validation FAILED: {error_msg}")
        return {
            "response": explain_error(error_msg),
            "missing_fields": [],
            "errors": [error_msg]
        }

    # 7. Execute operation
    print(f"[ORCHESTRATOR] Validation passed. Executing operation...")
    execution_result = execute_operation(planned, user)
    print(f"[ORCHESTRATOR] Execution result: {execution_result}")

    if not execution_result.get("success"):
        error_msg = execution_result.get("error", "Operation failed")
        state["last_error"] = error_msg
        save_session(session_id, state)
        print(f"[ORCHESTRATOR] Execution FAILED: {error_msg}")
        return {
            "response": explain_error(error_msg),
            "missing_fields": [],
            "errors": [error_msg]
        }

    # 8. Return success response
    print(f"[ORCHESTRATOR] Execution successful. Calling success explainer...")
    success_msg = success(execution_result)
    print(f"[ORCHESTRATOR] Success message: {success_msg[:200]}...")
    save_session(session_id, state)

    return {
        "response": success_msg,
        "missing_fields": [],
        "errors": []
    }
