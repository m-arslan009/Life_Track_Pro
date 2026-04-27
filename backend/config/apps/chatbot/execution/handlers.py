from config.apps.chatbot.schema.commands import ChatCommand
from config.apps.chatbot.execution.registry import ExecutionResult
from config.apps.chatbot.adapters.project_adapter import ProjectAdapter
from config.apps.chatbot.adapters.task_adapter import TaskAdapter
from config.apps.chatbot.adapters.milestone_adapter import MilestoneAdapter
from config.apps.chatbot.adapters.risk_adapter import RiskAdapter
from config.apps.chatbot.adapters.report_adapter import ReportAdapter


class ProjectHandler:
    def create(self, command, user_context):
        adapter = ProjectAdapter()
        return self._call_adapter(
            adapter.create,
            command.parameters,
            user_context,
        )

    def update(self, command, user_context):
        adapter = ProjectAdapter()
        return self._call_adapter(
            adapter.update,
            command.parameters,
            user_context,
        )

    def delete(self, command, user_context):
        adapter = ProjectAdapter()
        return self._call_adapter(
            adapter.delete,
            command.parameters,
            user_context,
        )

    def list(self, command, user_context):
        adapter = ProjectAdapter()
        return self._call_adapter(
            adapter.list,
            command.parameters,
            user_context,
        )

    def _call_adapter(self, method, parameters, user_context):
        from config.apps.chatbot.adapters.base import BaseAdapterError
        try:
            return method(parameters, user_context)
        except BaseAdapterError as e:
            return ExecutionResult(
                success=False,
                errors=[e.message],
                missing_fields=e.missing_fields,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[str(e)],
            )


class TaskHandler:
    def create(self, command, user_context):
        adapter = TaskAdapter()
        return self._call_adapter(
            adapter.create,
            command.parameters,
            user_context,
        )

    def update(self, command, user_context):
        adapter = TaskAdapter()
        return self._call_adapter(
            adapter.update,
            command.parameters,
            user_context,
        )

    def delete(self, command, user_context):
        adapter = TaskAdapter()
        return self._call_adapter(
            adapter.delete,
            command.parameters,
            user_context,
        )

    def list(self, command, user_context):
        adapter = TaskAdapter()
        return self._call_adapter(
            adapter.list,
            command.parameters,
            user_context,
        )

    def _call_adapter(self, method, parameters, user_context):
        from config.apps.chatbot.adapters.base import BaseAdapterError
        try:
            return method(parameters, user_context)
        except BaseAdapterError as e:
            return ExecutionResult(
                success=False,
                errors=[e.message],
                missing_fields=e.missing_fields,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[str(e)],
            )


class MilestoneHandler:
    def get(self, command, user_context):
        adapter = MilestoneAdapter()
        return self._call_adapter(
            adapter.get,
            command.parameters,
            user_context,
        )

    def _call_adapter(self, method, parameters, user_context):
        from config.apps.chatbot.adapters.base import BaseAdapterError
        try:
            return method(parameters, user_context)
        except BaseAdapterError as e:
            return ExecutionResult(
                success=False,
                errors=[e.message],
                missing_fields=e.missing_fields,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[str(e)],
            )


class RiskHandler:
    def create(self, command, user_context):
        adapter = RiskAdapter()
        return self._call_adapter(
            adapter.create,
            command.parameters,
            user_context,
        )

    def _call_adapter(self, method, parameters, user_context):
        from config.apps.chatbot.adapters.base import BaseAdapterError
        try:
            return method(parameters, user_context)
        except BaseAdapterError as e:
            return ExecutionResult(
                success=False,
                errors=[e.message],
                missing_fields=e.missing_fields,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[str(e)],
            )


class ReportHandler:
    def generate(self, command, user_context):
        adapter = ReportAdapter()
        return self._call_adapter(
            adapter.generate,
            command.parameters,
            user_context,
        )

    def _call_adapter(self, method, parameters, user_context):
        from config.apps.chatbot.adapters.base import BaseAdapterError
        try:
            return method(parameters, user_context)
        except BaseAdapterError as e:
            return ExecutionResult(
                success=False,
                errors=[e.message],
                missing_fields=e.missing_fields,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[str(e)],
            )


class HandlerRouter:
    _COMMAND_ACTION_MAP = {
        "create_project": ("ProjectHandler", "create"),
        "update_project": ("ProjectHandler", "update"),
        "delete_project": ("ProjectHandler", "delete"),
        "list_projects": ("ProjectHandler", "list"),
        "create_task": ("TaskHandler", "create"),
        "update_task": ("TaskHandler", "update"),
        "delete_task": ("TaskHandler", "delete"),
        "list_tasks": ("TaskHandler", "list"),
        "get_milestones": ("MilestoneHandler", "get"),
        "create_risk": ("RiskHandler", "create"),
        "generate_report": ("ReportHandler", "generate"),
    }

    def __init__(self):
        self._handlers = {
            "ProjectHandler": ProjectHandler(),
            "TaskHandler": TaskHandler(),
            "MilestoneHandler": MilestoneHandler(),
            "RiskHandler": RiskHandler(),
            "ReportHandler": ReportHandler(),
        }

    def route(self, command: ChatCommand, user_context: dict) -> ExecutionResult:
        mapping = self._COMMAND_ACTION_MAP.get(command.command)
        if not mapping:
            return ExecutionResult(
                success=False,
                errors=[f"Unknown command type: {command.command}"],
            )

        handler_name, action = mapping
        handler = self._handlers.get(handler_name)
        if not handler:
            return ExecutionResult(
                success=False,
                errors=[f"Handler not found: {handler_name}"],
            )

        method = getattr(handler, action, None)
        if not method:
            return ExecutionResult(
                success=False,
                errors=[f"Action '{action}' not found on {handler_name}"],
            )

        return method(command, user_context)