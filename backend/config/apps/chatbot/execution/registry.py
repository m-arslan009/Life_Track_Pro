from typing import Protocol, Callable, Dict
from dataclasses import dataclass, field
from config.apps.chatbot.schema.commands import ChatCommand


@dataclass
class ExecutionResult:
    success: bool
    result: dict | None = None
    errors: list[str] | None = None
    missing_fields: list[str] | None = None


class CommandHandler(Protocol):
    def handle(self, command: ChatCommand, user_context: dict) -> ExecutionResult:
        ...


class HandlerRegistry:
    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}

    def register(self, command_type: str, handler: CommandHandler) -> None:
        self._handlers[command_type] = handler

    def get(self, command_type: str) -> CommandHandler | None:
        return self._handlers.get(command_type)

    def unregister(self, command_type: str) -> None:
        self._handlers.pop(command_type, None)


def create_handler_registry() -> HandlerRegistry:
    from config.apps.chatbot.execution.handlers import (
        ProjectHandler,
        TaskHandler,
        MilestoneHandler,
        RiskHandler,
        ReportHandler,
    )
    registry = HandlerRegistry()
    registry.register("create_project", ProjectHandler())
    registry.register("update_project", ProjectHandler())
    registry.register("delete_project", ProjectHandler())
    registry.register("list_projects", ProjectHandler())
    registry.register("create_task", TaskHandler())
    registry.register("update_task", TaskHandler())
    registry.register("delete_task", TaskHandler())
    registry.register("list_tasks", TaskHandler())
    registry.register("get_milestones", MilestoneHandler())
    registry.register("create_risk", RiskHandler())
    registry.register("generate_report", ReportHandler())
    return registry