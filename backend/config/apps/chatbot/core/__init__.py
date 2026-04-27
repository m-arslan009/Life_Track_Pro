def get_controller():
    from config.apps.chatbot.core.controller import ChatController, UserContext
    return ChatController, UserContext


def __getattr__(name):
    if name == "ChatController":
        return get_controller()[0]
    if name == "UserContext":
        return get_controller()[1]
    raise AttributeError(f"module has no attribute {name}")


__all__ = ["ChatController", "UserContext"]