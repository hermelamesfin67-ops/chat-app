from django.urls import path
from .views import (
    ConversationListCreateView,
    ConversationDetailView,
    MessageListCreateView,
    MessageDetailView,
    UserListCreateView,

)

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view(), name='conversations'),
    path("conversations/<int:pk>/", ConversationDetailView.as_view(),
         name='conversation-detail'),
    path("users/", UserListCreateView.as_view(), name='users'),
    path("messages/", MessageListCreateView.as_view(), name='messages'),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name='message-detail'),
]
