import json
import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from config.apps.chatbot.schema.commands import ChatCommand


CAPABILITY_CONTRACT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "contracts", "capability.contract.json"
)
API_ENDPOINTS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "contracts", "api_endpoints.json"
)


def load_capability_contract() -> dict:
    with open(CAPABILITY_CONTRACT_PATH, "r") as f:
        return json.load(f)


def load_api_endpoints() -> dict:
    with open(API_ENDPOINTS_PATH, "r") as f:
        return json.load(f)


CONTRACT = load_capability_contract()
API_ENDPOINTS = load_api_endpoints()


COMMAND_TO_ACTION = {
    "create_project": "projects.createProject.post",
    "update_project": "projects.projectDetail.put",
    "delete_project": "projects.projectDetail.delete",
    "create_task": "tasks.taskListCreate.post",
    "update_task": "tasks.taskDetail.patch",
    "delete_task": "tasks.taskDetail.delete",
    "list_projects": "projects.getAllProjects.get",
    "list_tasks": "tasks.taskListCreate.get",
    "get_milestones": "milestones.milestoneListCreate.get",
    "create_risk": "risks.placeholder",
    "generate_report": "reports.reportsOverview.get",
}


ROLE_PERMISSIONS = {
    "manager": [
        "create_project",
        "update_project",
        "delete_project",
        "create_task",
        "update_task",
        "delete_task",
        "list_projects",
        "list_tasks",
        "get_milestones",
        "create_risk",
        "generate_report",
    ],
    "developer": [
        "create_project",
        "update_project",
        "create_task",
        "update_task",
        "delete_task",
        "list_projects",
        "list_tasks",
        "get_milestones",
        "create_risk",
        "generate_report",
    ],
    "viewer": [
        "list_projects",
        "list_tasks",
        "get_milestones",
        "generate_report",
    ],
}


COMMAND_REQUIRED_FIELDS = {
    "create_project": ["project_name"],
    "update_project": ["project_id"],
    "delete_project": ["project_id"],
    "create_task": ["title", "project"],
    "update_task": ["task_id"],
    "delete_task": ["task_id"],
    "list_projects": [],
    "list_tasks": [],
    "get_milestones": ["project"],
    "create_risk": ["project", "description"],
    "generate_report": [],
}


COMMAND_OPTIONAL_FIELDS = {
    "create_project": ["progress", "start_date", "due_date", "team_members"],
    "update_project": ["project_name", "project_description", "status", "progress", "start_date", "due_date", "team_members"],
    "delete_project": [],
    "create_task": ["description", "status", "assignee"],
    "update_task": ["title", "description", "status", "project", "milestone", "assignee"],
    "delete_task": [],
    "list_projects": ["status"],
    "list_tasks": ["status"],
    "get_milestones": ["status"],
    "create_risk": ["severity"],
    "generate_report": [],
}


VALID_STATUS_VALUES = {
    "projects.Projects": ["active", "on_track", "at_risk", "complete"],
    "tasks.Task": ["todo", "in_progress", "done", "blocked"],
    "milestones.Milestone": ["planned", "in_progress", "completed", "delayed"],
}


@dataclass
class ValidationContext:
    user_id: int
    username: str
    role: str


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    sanitized_command: Optional[ChatCommand]
    missing_fields: List[str] = field(default_factory=list)


class CommandValidator:
    def __init__(self, contract: Optional[dict] = None, api_endpoints: Optional[dict] = None):
        self.contract = contract or CONTRACT
        self.api_endpoints = api_endpoints or API_ENDPOINTS
        self._action_map = self._build_action_map()
        self._entity_map = self._build_entity_map()

    def _build_action_map(self) -> Dict[str, dict]:
        actions = {}
        for action in self.contract.get("actions", []):
            actions[action["id"]] = action
        return actions

    def _build_entity_map(self) -> Dict[str, dict]:
        entities = {}
        for entity in self.contract.get("entities", []):
            key = f"{entity['app']}.{entity['model']}"
            entities[key] = entity
        return entities

    def validate(
        self,
        command: ChatCommand,
        context: ValidationContext,
    ) -> ValidationResult:
        if not command:
            return ValidationResult(
                valid=False,
                errors=["Invalid command object"],
                sanitized_command=None,
            )

        command_name = command.command
        if not command_name:
            return ValidationResult(
                valid=False,
                errors=["Missing command name"],
                sanitized_command=None,
            )

        if command_name not in COMMAND_REQUIRED_FIELDS:
            return ValidationResult(
                valid=False,
                errors=[f"Unknown command: {command_name}"],
                sanitized_command=None,
            )

        role_errors = self._validate_role_permissions(command_name, context)
        if role_errors:
            return ValidationResult(
                valid=False,
                errors=role_errors,
                sanitized_command=None,
            )

        required_errors = self._validate_required_fields(command)
        if required_errors:
            return ValidationResult(
                valid=False,
                errors=required_errors,
                sanitized_command=None,
            )

        field_errors = self._validate_allowed_fields(command)
        if field_errors:
            return ValidationResult(
                valid=False,
                errors=field_errors,
                sanitized_command=None,
            )

        status_errors = self._validate_status_values(command)
        if status_errors:
            return ValidationResult(
                valid=False,
                errors=status_errors,
                sanitized_command=None,
            )

        return ValidationResult(
            valid=True,
            errors=[],
            sanitized_command=command,
        )

    def _validate_role_permissions(
        self,
        command_name: str,
        context: ValidationContext,
    ) -> List[str]:
        allowed = ROLE_PERMISSIONS.get(context.role, [])
        if command_name not in allowed:
            return [
                f"Role '{context.role}' is not permitted to execute '{command_name}'"
            ]
        return []

    def _validate_required_fields(self, command: ChatCommand) -> List[str]:
        required = COMMAND_REQUIRED_FIELDS.get(command.command, [])
        params = command.parameters
        missing = [f for f in required if f not in params or params.get(f) is None]
        if missing:
            return [f"Missing required field: {f}" for f in missing]
        return []

    def _validate_allowed_fields(self, command: ChatCommand) -> List[str]:
        allowed = set(COMMAND_REQUIRED_FIELDS.get(command.command, [])) | set(
            COMMAND_OPTIONAL_FIELDS.get(command.command, [])
        )
        params = command.parameters
        extra = [f for f in params if f not in allowed]
        if extra:
            return [f"Unknown field: {f}" for f in extra]
        return []

    def _validate_status_values(self, command: ChatCommand) -> List[str]:
        params = command.parameters
        errors = []

        if command.command == "create_project":
            if "status" in params and params["status"] not in VALID_STATUS_VALUES["projects.Projects"]:
                errors.append(f"Invalid status: {params['status']}")

        if command.command == "create_task":
            if "status" in params and params["status"] not in VALID_STATUS_VALUES["tasks.Task"]:
                errors.append(f"Invalid status: {params['status']}")

        if command.command == "update_task":
            if "status" in params and params["status"] not in VALID_STATUS_VALUES["tasks.Task"]:
                errors.append(f"Invalid status: {params['status']}")

        return errors