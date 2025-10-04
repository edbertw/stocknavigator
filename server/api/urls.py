# api/urls.py
from django.urls import path
from . import views
from .views import submit_stock
from .predict_views import predict_stock
from .rag_main import (
    ask_chatbot, 
    create_chat_session, 
    get_chat_session, 
    end_chat_session, 
    get_user_sessions, 
    cleanup_expired_sessions
)
from .sentiment import sen_display

urlpatterns = [
    path("notes/", views.NoteListCreate.as_view(), name="note-list"),
    path("notes/delete/<int:pk>/", views.NoteDelete.as_view(), name="delete-note"),
    
    # Stock analysis endpoints
    path('submit-stock/', submit_stock),
    path('predict-stock/', predict_stock),
    path('sen-display/', sen_display),
    
    # Chatbot endpoints
    path('ask-chatbot/', ask_chatbot),
    
    # Session management endpoints
    path('chat-sessions/', views.ChatSessionListCreate.as_view(), name='chat-session-list-create'),
    path('chat-sessions/<uuid:pk>/', views.ChatSessionDetail.as_view(), name='chat-session-detail'),
    path('chat-sessions/<uuid:session_id>/messages/', views.ChatMessageList.as_view(), name='chat-message-list'),
    path('user-chat-sessions/', views.UserChatSessions.as_view(), name='user-chat-sessions'),
    
    # Direct session management endpoints (from rag_main.py)
    path('create-chat-session/', create_chat_session, name='create-chat-session'),
    path('get-chat-session/<uuid:session_id>/', get_chat_session, name='get-chat-session'),
    path('end-chat-session/<uuid:session_id>/', end_chat_session, name='end-chat-session'),
    path('get-user-sessions/<int:user_id>/', get_user_sessions, name='get-user-sessions'),
    path('cleanup-expired-sessions/', cleanup_expired_sessions, name='cleanup-expired-sessions'),
    
    # Monitoring endpoints
    path('metrics/', views.metrics, name='metrics'),
]
