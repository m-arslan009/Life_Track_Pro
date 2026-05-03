from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .orchestrator import handle_message


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    message = request.data.get('message', '')
    session_id = request.data.get('session_id', '')

    print("\n" + "="*60)
    print("CHATBOT REQUEST RECEIVED")
    print("="*60)
    print(f"USER: {request.user.username} (ID: {request.user.id})")
    print(f"SESSION_ID: {session_id}")
    print(f"USER MESSAGE: {message}")
    print("-"*60)

    if not message or not session_id:
        return Response(
            {'detail': 'message and session_id are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    result = handle_message(message, session_id, user=request.user)
    
    print("-"*60)
    print("FINAL RESPONSE TO FRONTEND:")
    print(f"  response: {result.get('response', '')[:200]}...")
    print(f"  missing_fields: {result.get('missing_fields', [])}")
    print(f"  errors: {result.get('errors', [])}")
    print("="*60 + "\n")
    
    return Response(result, status=status.HTTP_200_OK)
