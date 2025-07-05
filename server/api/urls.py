# api/urls.py
from django.urls import path
from . import views
from .views import submit_stock
from .predict_views import predict_stock
from .rag_main import ask_chatbot
from .sentiment import sen_display

urlpatterns = [
    path("notes/", views.NoteListCreate.as_view(), name="note-list"),
    path("notes/delete/<int:pk>/", views.NoteDelete.as_view(), name="delete-note"),
    
    path('submit-stock/', submit_stock),
    path('predict-stock/', predict_stock),
    path('ask-chatbot/', ask_chatbot),
    path('sen-display/', sen_display),
]
