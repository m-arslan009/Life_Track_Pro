from config.apps.chatbot.schema.commands import ChatCommand
from config.apps.chatbot.execution.registry import ExecutionResult, create_handler_registry
from config.apps.chatbot.execution.handlers import HandlerRouter


class CommandExecutor:
    def __init__(self, router: HandlerRouter | None = None):
        self._router = router or HandlerRouter()

    def execute(self, command: ChatCommand, user_context: dict) -> ExecutionResult:
        return self._router.route(command, user_context)