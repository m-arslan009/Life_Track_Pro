from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
import uuid
import logging

logger = logging.getLogger(__name__)


def _get_controller():
    from config.apps.chatbot.core.controller import ChatController, UserContext
    return ChatController, UserContext


@csrf_exempt
@require_POST
def chat(request):
    request_id = str(uuid.uuid4())[:8]
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.warning(f"[{request_id}] Invalid JSON in request")
        return JsonResponse({"error": "Invalid JSON", "request_id": request_id}, status=400)

    user_input = data.get("message", "")
    session_id = data.get("session_id", "default")

    user = request.user if request.user.is_authenticated else None

    if not user:
        logger.warning(f"[{request_id}] Anonymous request accepted - using default user")
        user_id = data.get("user_id", 1)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None
        if not user:
            user = User.objects.first()
        if not user:
            return JsonResponse({"error": "No user found", "request_id": request_id}, status=401)

    logger.info(f"[{request_id}] Processing: user={user.username}, input={user_input[:50]}")

    ChatController, UserContext = _get_controller()
    
    user_context = UserContext(
        user_id=user.id,
        username=user.username,
        role=getattr(user, 'role', 'developer'),
        session_id=session_id,
    )

    controller = ChatController()
    response = controller.process(user_input, user_context)

    logger.info(f"[{request_id}] Completed: executed={response.executed}")

    return JsonResponse({
        "response": response.reply,
        "executed": response.executed,
        "missing_fields": response.missing_fields,
        "errors": [],
        "context": response.context,
        "request_id": request_id,
    })


def health(request):
    return JsonResponse({"status": "ok"})