from .views import websocket_test
from django.urls import path
from .views import (
    ConversationListCreateView,
    ConversationDetailView,
    MessageListCreateView,
    MessageDetailView,
    PhoneLoginView,
    UserSignUpView,
    ProfileView,
    LogoutView

)

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', PhoneLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='my-profile'),
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path("test/", websocket_test, name="test"),

    path("conversations/", ConversationListCreateView.as_view(), name='conversations'),
    path("conversations/<int:pk>/", ConversationDetailView.as_view(),
         name='conversation-detail'),
    path("messages/", MessageListCreateView.as_view(), name='messages'),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name='message-detail'),
    path("logout/", LogoutView.as_view(), name='logout'),
]


