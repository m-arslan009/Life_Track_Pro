from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatResponse:
    reply: str
    executed: bool
    missing_fields: list[str] | None = None
    context: dict | None = None


FOLLOW_UP_TEMPLATES = {
    "create_project": {
        "project_name": "What should the project be named?",
        "project_description": "Please provide a description for the project.",
        "status": "What status should the project have?",
    },
    "create_task": {
        "title": "What is the task title?",
        "project": "Which project should this task belong to?",
        "milestone": "Which milestone is this task for?",
    },
    "update_task": {
        "task_id": "Which task would you like to update?",
    },
    "list_tasks": {
        "project": "Which project's tasks would you like to see?",
    },
    "get_milestones": {
        "project": "Which project's milestones are you interested in?",
    },
    "create_risk": {
        "project_id": "Which project does this risk relate to?",
        "description": "Please describe the risk.",
    },
    "generate_report": {
        "project_id": "Which project should the report be for?",
    },
}


def generate_follow_up(command: str, missing_fields: list[str]) -> str:
    if not missing_fields:
        return "I need more information. Could you please provide more details?"

    prompts = []
    for field in missing_fields:
        prompt = FOLLOW_UP_TEMPLATES.get(command, {}).get(field)
        if prompt:
            prompts.append(prompt)
        else:
            prompts.append(f"Please provide: {field}")

    if len(prompts) == 1:
        return prompts[0]
    return "I need a few more details: " + " ".join(prompts)