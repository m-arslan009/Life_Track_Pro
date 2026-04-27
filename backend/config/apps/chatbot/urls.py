from django.urls import path
from config.apps.chatbot.views import chat, health

urlpatterns = [
    path("", chat, name="chatbot_chat"),
    path("health/", health, name="chatbot_health"),
    
]