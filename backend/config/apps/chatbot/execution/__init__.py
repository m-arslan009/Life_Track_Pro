def __getattr__(name):
    if name == "CommandExecutor":
        from config.apps.chatbot.execution.executor import CommandExecutor
        from config.apps.chatbot.execution.handlers import HandlerRouter
        from config.apps.chatbot.execution.registry import ExecutionResult
        return ExecutionResult
    raise AttributeError(f"module has no attribute {name}")


__all__ = ["CommandExecutor", "HandlerRouter", "ExecutionResult"]   