from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union


class CommandType:
    CREATE_PROJECT = "create_project"
    UPDATE_PROJECT = "update_project"
    DELETE_PROJECT = "delete_project"
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    LIST_PROJECTS = "list_projects"
    LIST_TASKS = "list_tasks"
    GET_MILESTONES = "get_milestones"
    CREATE_RISK = "create_risk"
    GENERATE_REPORT = "generate_report"
    UNKNOWN = "unknown"


VALID_COMMANDS = [
    CommandType.CREATE_PROJECT,
    CommandType.UPDATE_PROJECT,
    CommandType.DELETE_PROJECT,
    CommandType.CREATE_TASK,
    CommandType.UPDATE_TASK,
    CommandType.DELETE_TASK,
    CommandType.LIST_PROJECTS,
    CommandType.LIST_TASKS,
    CommandType.GET_MILESTONES,
    CommandType.CREATE_RISK,
    CommandType.GENERATE_REPORT,
]


@dataclass
class ChatCommand:
    command: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentParseResult:
    command: Optional[ChatCommand]
    missing_fields: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    raw_text: Optional[str] = None
    
    @property
    def is_raw(self) -> bool:
        return self.raw_text is not None and self.command is None
    
    @property
    def is_command(self) -> bool:
        return self.command is not None
    
    @property
    def reason(self) -> Optional[str]:
        if self.raw_text is not None:
            if self.errors:
                return self.errors[0]
            return "unknown_intent"
        return None